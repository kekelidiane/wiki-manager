from sqlmodel import SQLModel

#comment below is to solve the error < missing-import >
# pyrefly: ignore [missing-import]
from src.app.models.wiki import (
    Category,
    Media,
    Article,
    Comment,
    ArticleReaction,
    Status,
    ReactionType,
)

def test_metadata_contains_all_seven_tables():
# names matching exactly the table_name attributes of models
    expected_tables = {
        "categories",
        "medias",
        "comments",
        "article_reactions",
        "articles",
        "article_categories",
        "article_medias_gallery",
    }
    assert expected_tables.issubset(SQLModel.metadata.tables.keys())

def test_instantiation_and_exclusions():
    category = Category(
        category_id="cat-123",
        title="Mango",
        description="delicious yellow fruit from Togo",
        created_by="dia",
    )
    dump_cat = category.model_dump()
    assert "id" not in dump_cat
    assert dump_cat["category_id"] == "cat-123"

    article = Article(
        article_id="art-999",
        title="Pstudio c'est génial",
        content="Corps de l'article",
        state=Status.DRAFT,
        user_id="dia",
        created_by="dia",
        tags=["python", "sqlmodel"],
    )
    dump_art = article.model_dump()
    assert "id" not in dump_art
    assert "is_deleted" not in dump_art
    assert dump_art["state"] == Status.DRAFT

    comment = Comment(
        comment_id="com-111",
        content="Super article!",
        article_id="art-999",
        created_by="mich",
        is_deleted=True,
    )
    dump_com = comment.model_dump()
    assert "id" not in dump_com
    assert "is_deleted" not in dump_com

    reaction = ArticleReaction(
        reaction_id="react-001",
        article_id="art-999",
        user_id="kekeli",
        reaction=ReactionType.LIKE,
        created_by="kekeli",
    )
    dump_react = reaction.model_dump()
    assert dump_react["reaction"] == ReactionType.LIKE