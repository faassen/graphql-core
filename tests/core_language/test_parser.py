from pytest import raises
from graphql.core.language.error import LanguageError
from graphql.core.language.location import SourceLocation
from graphql.core.language.source import Source
from graphql.core.language.parser import parse, Loc
from graphql.core.language import ast
from .fixtures import KITCHEN_SINK


def test_parse_provides_useful_errors():
    with raises(LanguageError) as excinfo:
        parse("""{""")
    assert (
               u'Syntax Error GraphQL (1:2) Expected Name, found EOF\n'
               u'\n'
               u'1: {\n'
               u'    ^\n'
               u''
           ) == excinfo.value.message

    assert excinfo.value.positions == [1]
    assert excinfo.value.locations == [SourceLocation(line=1, column=2)]

    with raises(LanguageError) as excinfo:
        parse("""{ ...MissingOn }
fragment MissingOn Type
""")
    assert 'Syntax Error GraphQL (2:20) Expected "on", found Name "Type"' in str(excinfo.value)

    with raises(LanguageError) as excinfo:
        parse('{ field: {} }')
    assert 'Syntax Error GraphQL (1:10) Expected Name, found {' in str(excinfo.value)

    with raises(LanguageError) as excinfo:
        parse('notanoperation Foo { field }')
    assert 'Syntax Error GraphQL (1:1) Unexpected Name "notanoperation"' in str(excinfo.value)

    with raises(LanguageError) as excinfo:
        parse('...')
    assert 'Syntax Error GraphQL (1:1) Unexpected ...' in str(excinfo.value)


def test_parse_provides_useful_error_when_using_source():
    with raises(LanguageError) as excinfo:
        parse(Source('query', 'MyQuery.graphql'))
    assert 'Syntax Error MyQuery.graphql (1:6) Expected {, found EOF' in str(excinfo.value)


def test_parses_variable_inline_values():
    parse('{ field(complex: { a: { b: [ $var ] } }) }')


def test_parses_constant_default_values():
    with raises(LanguageError) as excinfo:
        parse('query Foo($x: Complex = { a: { b: [ $var ] } }) { field }')
    assert 'Syntax Error GraphQL (1:37) Unexpected $' in str(excinfo.value)


def test_does_not_accept_fragments_named_on():
    with raises(LanguageError) as excinfo:
        parse('fragment on on on { on }')

    assert 'Syntax Error GraphQL (1:10) Unexpected Name "on"' in excinfo.value.message


def test_does_not_accept_fragments_spread_of_on():
    with raises(LanguageError) as excinfo:
        parse('{ ...on }')

    assert 'Syntax Error GraphQL (1:9) Expected Name, found }' in excinfo.value.message


def test_does_not_allow_null_value():
    with raises(LanguageError) as excinfo:
        parse('{ fieldWithNullableStringInput(input: null) }')

    assert 'Syntax Error GraphQL (1:39) Unexpected Name "null"' in excinfo.value.message


def test_parses_multi_byte_characters():
    result = parse(u'''
        # This comment has a \u0A0A multi-byte character.
        { field(arg: "Has a \u0A0A multi-byte character.") }
    ''', no_location=True, no_source=True)
    assert result == ast.Document(
        definitions=[
            ast.OperationDefinition(
                operation='query', name=None, variable_definitions=None, directives=[],
                selection_set=ast.SelectionSet(
                    selections=[
                        ast.Field(
                            alias=None, name=ast.Name(value=u'field'),
                            arguments=[
                                ast.Argument(
                                    name=ast.Name(value=u'arg'),
                                    value=ast.StringValue(value=u'Has a \u0a0a multi-byte character.'))],
                            directives=[], selection_set=None)
                    ]
                )
            )
        ]
    )


def tesst_allows_non_keywords_anywhere_a_name_is_allowed():
    non_keywords = [
        'on',
        'fragment',
        'query',
        'mutation',
        'true',
        'false'
    ]

    query_template = '''
    query {keyword} {
        ... {fragment_name}
        ... on {keyword} { field }
    }
    fragment {fragment_name} on Type {
        {keyword}({keyword}: ${keyword}) @{keyword}({keyword}: {keyword})
    }
    '''

    for keyword in non_keywords:
        fragment_name = keyword
        if keyword == 'on':
            fragment_name = 'a'

        parse(query_template.format(fragment_name=fragment_name, keyword=keyword))


def test_parses_kitchen_sink():
    parse(KITCHEN_SINK)


def parses_experimental_subscription_feature():
    parse('''
        subscription Foo {
            subscriptionField
        }
    ''')


def test_parses_anonymous_operations():
    parse('''
        mutation {
            mutationField
        }
    ''')


def test_parse_creates_ast():
    source = Source("""{
  node(id: 4) {
    id,
    name
  }
}
""")
    result = parse(source)

    assert result == \
           ast.Document(
               loc=Loc(start=0, end=41, source=source),
               definitions=
               [ast.OperationDefinition(
                   loc=Loc(start=0, end=40, source=source),
                   operation='query',
                   name=None,
                   variable_definitions=None,
                   directives=[],
                   selection_set=ast.SelectionSet(
                       loc=Loc(start=0, end=40, source=source),
                       selections=
                       [ast.Field(
                           loc=Loc(start=4, end=38, source=source),
                           alias=None,
                           name=ast.Name(
                               loc=Loc(start=4, end=8, source=source),
                               value='node'),
                           arguments=[ast.Argument(
                               name=ast.Name(loc=Loc(start=9, end=11, source=source),
                                             value='id'),
                               value=ast.IntValue(
                                   loc=Loc(start=13, end=14, source=source),
                                   value='4'),
                               loc=Loc(start=9, end=14, source=source))],
                           directives=[],
                           selection_set=ast.SelectionSet(
                               loc=Loc(start=16, end=38, source=source),
                               selections=
                               [ast.Field(
                                   loc=Loc(start=22, end=24, source=source),
                                   alias=None,
                                   name=ast.Name(
                                       loc=Loc(start=22, end=24, source=source),
                                       value='id'),
                                   arguments=[],
                                   directives=[],
                                   selection_set=None),
                                   ast.Field(
                                       loc=Loc(start=30, end=34, source=source),
                                       alias=None,
                                       name=ast.Name(
                                           loc=Loc(start=30, end=34, source=source),
                                           value='name'),
                                       arguments=[],
                                       directives=[],
                                       selection_set=None)]))]))])
