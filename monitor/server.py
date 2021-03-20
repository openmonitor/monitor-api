import falcon


class Monitor:

    def on_get(self, req, resp):
        # select frames from db, parse to json, return
        pass


class Comment:

    def on_post(self, req, resp):
        # auth, insert comment
        pass

    def on_update(self, req, resp):
        # insert comment update
        pass


def create():
    api = falcon.API()
    api.add_route('/', Monitor())
    api.add_route('/comment', Comment())
    return api


application = create()
