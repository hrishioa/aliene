from gpt import parse_user_command
from models.Command import MaybeUserCommand, Translation, Query

def test_translation_request():
    sample_translation = "Can you translate the following phrase for me? - Où est l'hôtel de ville? Je dois soumettre un document très important d'ici aujour'hui?"
    sample_translation_2 = "明天的天气真的是太好了！看起来我们可以踢足球。"

    translations = [
        sample_translation,
        sample_translation_2
    ]

    for translation in translations:
        response: MaybeUserCommand = parse_user_command(translation)
        assert response.result is not None, response.message
        assert isinstance(response.result.command, Translation)


def test_query_request():
    sample_query = "What's the closest city in Europe that I can get to from Singapore"
    sample_query_2 = "What would go well today with the shirt that I'm wearing?"

    queries = [sample_query, sample_query_2]

    for query in queries:
        response: MaybeUserCommand = parse_user_command(query)

        assert response.result is not None, response.message
        assert isinstance(
            response.result.command, Query
        ), f"Response was of the wrong type of {response.result.command.__class__}"

def test_ambigious_query():
    sample_ambigious_query = "Fast and extensible, Pydantic plays nicely with your linters/IDE/brain. Define how data should be in pure, canonical Python 3.7+; validate it with Pydantic."
    sample_ambigious_query_2 = "Large-language models cost quite a bit of money to run. To grow Cursor sustainably without compromising our service quality, we need to cover our costs."

    queries = [sample_ambigious_query, sample_ambigious_query_2]

    for query in queries:
        response: MaybeUserCommand = parse_user_command(query)

        assert response.result is None


