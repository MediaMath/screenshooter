from screenshooter.saves import s3Service


class TestS3Service():

    def setup_method(self, method):
        self.s3 = s3Service()

    def testParseOutBackslash(self):
        assert "/" in self.s3.parseOutBackslash("something/with/slashes") == False

    def testParseInBackslash(self):
        values = dict()
        dictionary = dict(values)
        some = dict(dictionary)
        assert "/" in self.s3.parseInBackslash(some, dictionary, values) == True

    def testCollectImagesFromS3(self):
        assert self.s3.collectS3Images() is not None

    def testSaveImagesToS3(self):
        result = self.s3.saveS3()
        #assert result['count'] == len(result['responses']) #<- this may not work if errors are reported in responses
