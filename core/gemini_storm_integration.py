import logging

from api.models import ArticleData
from storm.knowledge_storm import STORMWikiRunnerArguments, STORMWikiLMConfigs
from storm.knowledge_storm.lm import GoogleModel
from storm.knowledge_storm.rm import SerperRM
from storm.knowledge_storm.storm_wiki.engine import STORMWikiRunner
from storm.knowledge_storm.storm_wiki.modules.callback import BaseCallbackHandler

logger = logging.getLogger(__name__)


def run_storm(topic: str, google_api_key: str, serper_api_key: str) -> ArticleData:
    """
    Execute the STORM pipeline using Gemini and Serper for the given topic.
    Requires Google and Serper API keys to be passed explicitly.
    """
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY must be provided to run_storm function")
    if not serper_api_key:
        raise ValueError("SERPER_API_KEY must be provided to run_storm function")

    logger.info(f"Running STORM with Gemini and Serper for topic: {topic}")

    args = STORMWikiRunnerArguments(
        output_dir=".",
        max_conv_turn=1,
        max_perspective=1,
        max_search_queries_per_turn=1,
        disable_perspective=True,
        search_top_k=1,
        retrieve_top_k=1,
        max_thread_num=1,
    )
    lm_configs = STORMWikiLMConfigs()

    gemini_kwargs = {"api_key": google_api_key}

    conv_simulator_lm = GoogleModel(
        model="models/gemini-1.5-flash-002", max_tokens=500, **gemini_kwargs
    )
    question_asker_lm = GoogleModel(
        model="models/gemini-1.5-flash-002", max_tokens=500, **gemini_kwargs
    )

    outline_gen_lm = GoogleModel(
        model="models/gemini-2.0-flash-exp", max_tokens=400, **gemini_kwargs
    )
    article_gen_lm = GoogleModel(
        model="models/gemini-2.0-flash-lite-preview-02-05",
        max_tokens=700,
        **gemini_kwargs,
    )
    article_polish_lm = GoogleModel(
        model="models/gemini-2.0-flash-thinking-exp-01-21",
        max_tokens=4000,
        **gemini_kwargs,
    )

    lm_configs.set_conv_simulator_lm(conv_simulator_lm)
    lm_configs.set_question_asker_lm(question_asker_lm)
    lm_configs.set_outline_gen_lm(outline_gen_lm)
    lm_configs.set_article_gen_lm(article_gen_lm)
    lm_configs.set_article_polish_lm(article_polish_lm)

    retriever = SerperRM(serper_search_api_key=serper_api_key)

    runner = STORMWikiRunner(args, lm_configs, retriever)
    runner.topic = topic

    callback_handler = BaseCallbackHandler()
    info_table, conv_log = runner.storm_knowledge_curation_module.research(
        topic=topic,
        ground_truth_url="",
        callback_handler=callback_handler,
        max_perspective=args.max_perspective,
        disable_perspective=False,
        return_conversation_log=True,
    )
    logger.debug("Completed knowledge curation.")

    outline_article, draft_outline = (
        runner.storm_outline_generation_module.generate_outline(
            topic=topic,
            information_table=info_table,
            return_draft_outline=True,
            callback_handler=callback_handler,
        )
    )
    logger.debug("Generated outline.")

    draft_article = runner.storm_article_generation.generate_article(
        topic=topic,
        information_table=info_table,
        article_with_outline=outline_article,
        callback_handler=callback_handler,
    )
    logger.debug("Generated draft article.")

    final_article = runner.storm_article_polishing_module.polish_article(
        topic=topic, draft_article=draft_article, remove_duplicate=False
    )
    logger.debug("Polished the article.")

    return ArticleData(article=final_article.to_string())
