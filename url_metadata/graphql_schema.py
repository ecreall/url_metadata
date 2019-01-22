# -*- coding: utf-8 -*-
import graphene
from graphene import relay
import sqlite3

from .utils import add_url_metadata


DB_FILENAME = 'var/urls.db'


url_data_keys = [
    'url',
    'html',
    'title',
    'description',
    'thumbnail_url',
    'provider_name',
    'favicon_url',
    'author_name',
    'author_avatar',
    'data'
]


def extract_url_metadata(url_metadata):
    result = {}
    for key in url_data_keys:
        result[key] = url_metadata.get(key, None)

    return result


class UrlData(graphene.ObjectType):

    class Meta(object):
        interfaces = (relay.Node, )

    label = graphene.String()
    data = graphene.String()


class Url(graphene.ObjectType):

    class Meta(object):
        interfaces = (relay.Node, )

    url = graphene.String()
    html = graphene.String()
    title = graphene.String()
    description = graphene.String()
    thumbnail_url = graphene.String()
    provider_name = graphene.String()
    favicon_url = graphene.String()
    author_name = graphene.String()
    author_avatar = graphene.String()
    data = graphene.List(UrlData)

    def resolve_data(self, info, **args):  # pylint: disable=W0613
        return [UrlData(**entry) for entry in self.data]


class Query(graphene.ObjectType):

    metadata = graphene.Field(Url, url=graphene.String())

    def resolve_metadata(self, info, **args):  # pylint: disable=W0613
        url = args.get('url', None)
        if not url: return None
        with sqlite3.connect(DB_FILENAME) as conn:
            try:
                cursor = conn.cursor()
                url_metadata = add_url_metadata(url, cursor)
                return Url(**extract_url_metadata(url_metadata))
            except Exception:
                pass

        return None


schema = graphene.Schema(query=Query)


if __name__ == '__main__':
    import json
    schema_dict = {'data': schema.introspect()}
    with open('schema.json', 'w') as outfile:
        json.dump(schema_dict, outfile)
