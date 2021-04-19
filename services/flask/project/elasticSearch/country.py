from elasticsearch_dsl import Document, Long, Keyword, Text, Index
from elasticsearch_dsl.query import Match, MatchPhrasePrefix, Term, Bool, MultiMatch

countryIndex = Index('country')


@countryIndex.document
class CountryESModel(Document):
    id = Keyword()
    name = Text(fields={'raw': Keyword()})
    alpha2Code = Keyword()
    capital = Text()
    population = Long()
    region = Keyword()


def init():
    # delete the index, ignore if it doesn't exist
    countryIndex.delete(ignore=404)

    countryIndex.settings(number_of_shards=1)
    countryIndex.create()


def index_country(data):
    CountryESModel(
        meta={'id': data['id']},
        id=data['id'],
        name=data['name'],
        alpha2Code=data['alpha2Code'],
        capital=data['capital'],
        population=data['population'],
        region=data['region']
    ).save()

    # refresh index manually to make changes live
    countryIndex.refresh()


class CountrySearch:
    def __init__(self):
        pass

    @classmethod
    def compute_limit(cls, start_index):
        page_size = 10
        return page_size + start_index

    @classmethod
    def search(cls, searchInput):
        name = searchInput.get('name')  # optional field
        region = searchInput.get('region')  # optional field
        start_index = searchInput.get('offset')
        limit = cls.compute_limit(start_index)
        query = ''
        if name and region is None:
            query = MatchPhrasePrefix(name={"query": name})

        if name is None and region:
            query = Term(region={"value": region})

        if name and region:
            query = Bool(
                # should=[{"match": {"name": {"query": name, "fuzziness": "AUTO"}}}],
                # should=[Match(name={"query": name, "fuzziness": "AUTO"})],
                must=[MatchPhrasePrefix(name={"query": name})],
                filter={"term": {"region": region}},
            )

        s = CountryESModel.search()
        results = s[start_index:limit].query(query).execute()
        return [country.to_dict() for country in results]

    # @classmethod
    # def search_by_name(cls, name, offset):
    #     start_index = cls.compute_start_index(offset)
    #     limit = cls.compute_limit(start_index)
    #     s = CountryESModel.search()
    #     # query = Match(name={"query": name, "fuzziness": "AUTO"})
    #     query = MatchPhrasePrefix(name={"query": name})
    #     results = s[start_index:limit].query(query).execute()
    #     return [country.to_dict() for country in results]
    #
    # @classmethod
    # def search_by_region(cls, name, offset):
    #     start_index = cls.compute_start_index(offset)
    #     limit = cls.compute_limit(start_index)
    #     s = CountryESModel.search()
    #     results = s[start_index:limit].query("term", region=name).execute()
    #     return [country.to_dict() for country in results]
