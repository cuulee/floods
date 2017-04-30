import requests
import geojson
import logging
import os
import time
import homura
import shutil
import hashlib
from dateutil.relativedelta import relativedelta

from resources import util
from resources.notifications.notify import notify as notifyAPI

from urllib.parse import urljoin
from datetime import date, datetime, timedelta


class APIError(Exception):

    def __init__(self, status=None, mess=None, body=None):

        self.status = status
        self.mess = mess
        self.body = body
        pass

    def __str__(self):
        return 'HTTP Status: {}. {}'.format(self.status, self.mess)

class API(object):
    sleep = 30
    options = {'ground':"productType:GRD"}
    def __init__(self, user, passw, url='https://scihub.copernicus.eu/apihub/', notify = False):
        self.logger = logging.getLogger('SentinelAPI')

        if notify:
            self.notifications = True
            self.notify = notifyAPI.getNotify()
        else: self.notifications = False

        self.sesh = requests.Session()
        self.sesh.auth =  (user, passw)
        self.pageSize = 100
        self.url = url if url.endswith('/') else url + '/'

    def query(self,locale, option = None, startDate=None, endDate=datetime.now(), **kwards):
        if not option:
            option = self.options['ground']
        else:
            try:
                option = self.options[option]
            except KeyError as e:
                print('%s is not a correct option, using default' % e)
                option = self.options['ground']



        locale = self.getCoords(locale)
        query = self.formatQuery(locale, option, startDate, endDate, **kwards)
        return self.runQuery(query)

    def runQuery(self,query, startRow=0):
        url = self.formatURL(startRow=startRow)
        response = self.sesh.post(url, dict(q=query), auth=self.sesh.auth)
        self.checkResponse(response)
        try:
            jsonFeed = response.json()['feed']
            totalResults = int(jsonFeed['opensearch:totalResults'])
        except (ValueError, KeyError):
            raise APIError(response.status_code,
                           mess='Response not valid',
                           body=response.content)

        entries = jsonFeed.get('entry',[])

        #Check if only one product was returned
        if isinstance(entries,dict):
            entries = [entries]

        output = entries

        #Check if there are more pages of results left to get
        if totalResults > startRow + self.pageSize - 1:
            output += self.runQuery(query,startRow=(startRow+self.pageSize))
        return output

    def formatQuery(self,locale, option, startDate=None, endDate=datetime.now(), **kwargs):
        if startDate is None:
            startDate = self.formatDate(endDate - timedelta(hours=24) )

        else: startDate = self.formatDate(startDate)
        endDate = self.formatDate(endDate)
        acqisitionDate =  '(beginPosition:[%s TO %s])' % (startDate, endDate)
        queryLocale =  'AND (footprint:"Intersects(POLYGON((%s)))")'  % locale

        filters = ''
        filters += ' AND %s' % option

        for key in kwargs.keys():
            filters += ' AND (%s:%s)' % (key, kwargs[key])

        query = acqisitionDate + queryLocale + filters
        return query

    def formatURL(self, startRow=0):
        startQuery = 'search?format=json&rows={rows}&start={start}'.format(
        rows=self.pageSize, start=startRow)
        return urljoin(self.url, startQuery)

    def download(self, products,locale = None, path =None, maxTries = 5):
        if isinstance(products,dict):
            products = [products]
        self.logger.info('Downloading %d images' % len(products))

        if self.notifications:
            self.notify.push('Downloading %d images' % (len(products)))


        results = {}
        for i, product in enumerate(products):
            downloaded = False
            tries = maxTries
            while not downloaded and tries > 0:
                try:
                    outputPath, info = self.downloadProduct(product['id'],locale, path)
                    downloaded = True
                except(KeyboardInterrupt, SystemExit ):
                    raise
                except:
                    self.logger.exception('Error downloading %s' % product['title'])
                tries -= 1
            try:
                results[outputPath] = info
            except(UnboundLocalError):
                self.logger.info('Error downloading %s' % (product['id']))
            self.logger.info('%d of %d images downloaded' % (i+1, len(products)))
            if self.notifications and (i+1) %5== 0:
                self.notify.push('%d of %d images downloaded' % (i+1, len(products)))
        if self.notifications:
            self.notify.push('%d images downloaded' % len(results))
        return results

    def downloadProduct(self, id,locale = None, path = None):
        info = None
        while info is None:
            try:
                info = self.getOData(id)
            except APIError as e:
                self.logger.info('API error: %s \n Waiting %d seconds.' % (str(e),self.sleep))
                time.sleep(self.sleep)
        if path is None:
            outputPath = util.checkFolder('SentinelAPI', Output=True)
            year =datetime.strptime(info['date'], '%Y-%m-%dT%H:%M:%SZ').year
            outputName = info['name'] + '.zip'

            #             oldPath = os.path.join(outputPath, outputName)
            if locale:
                outputPath = util.checkFolder(locale, path=outputPath)
            outputPath = util.checkFolder(year, path=outputPath )
            outputPath = os.path.join(outputPath, outputName)
        else: outputPath = path


        if os.path.exists(outputPath) and os.path.getsize(outputPath) == info['size']:
            # check if md5 matches with server
            if self.compareMD5(outputPath,info['md5']):
                self.logger.info('%s was already found.' % outputPath)
                return outputPath, info
            else:
                self.logger.info('%s was not downloaded correctly' % outputPath)
                os.remove(outputPath)

        #
        # if os.path.exists(outputPath):
        #     self.logger.info('%s was already found.' % outputPath)
        #     return outputPath, info

        homura.download(info['url'],path = outputPath, auth=self.sesh.auth)

        return outputPath,info

    def getOData(self,id):
        url = urljoin(self.url, "odata/v1/Products('%s')/?$format=json" % id)
        response = self.sesh.get(url)
        self.checkResponse(response)

        d = response.json()['d']

        url = urljoin(self.url, "odata/v1/Products('%s')/$value" % id)
        info = {'id': d['Id'],
                'name': d['Name'],
                'size': int(d['ContentLength']),
                'md5': d['Checksum']['Value'],
                'date': self.getTime(d['ContentDate']['Start']),
                'url': url}
        return info

    @staticmethod
    def getTime(date):
        tmp = int(date.replace('/Date(','').replace(')/', '') ) /1000
        tmp= datetime.utcfromtimestamp(tmp)
        return API.formatDate(tmp)

    @staticmethod
    def formatDate(inputDate):
        if type(inputDate) == datetime or type(inputDate) == date:
            return inputDate.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            try:
                return datetime.strptime(inputDate, '%Y%m%d').strftime('%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                return inputDate

    @staticmethod
    def checkResponse(response):
        pass
        try:
            response.raise_for_status()
            response.json()
        except( requests.HTTPError, ValueError) as e:
            mess = 'Response not valid'
        #             try:
            try:
                mess = response.json()['error']['message']['value']
            except:
                if not response.text.rstrip().startswith('{'):
                    try:
                        h = html2text.HTML2Text()
                        h.ignore_images = True
                        h.ignore_anchors = True
                        msg = h.handle(response.text).strip()
                    except:
                        pass
            raise APIError(response.status_code,
                           mess=mess,
                           body=response.content)

    @staticmethod
    def getCoords(file, featureNumber=0):

        geojson_obj = geojson.loads(open(file, 'r').read())
        coordinates = geojson_obj['features'][featureNumber]['geometry']['coordinates'][0]
        # coordinates = geojson_obj['features'][2]['geometry']['coordinates']


        coordinates = ['%.5f %.5f' % (coord[0], coord[1]) for coord in coordinates]
        return ','.join(coordinates)

    @staticmethod
    def compareMD5(filePath, serverChecksum):
        print('Comparing %s' %filePath)
        hash = hashlib.md5()
        with open(filePath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)
        localChecksum = hash.hexdigest()
        return localChecksum.lower() == serverChecksum.lower()
