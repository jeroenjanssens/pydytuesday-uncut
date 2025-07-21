# repo name
# repo stars
# issue date
# issue comments
# issue labels
# issue pull_request
# 
 
import polars as pl
from glob import glob

filenames = glob("data/github_repos/*.json")


def read_github_json(filename):
    return (
        pl.read_json(filename)
        .unnest("metadata")
        .select("full_name", "stargazers_count", "issues")
        .explode("issues")
        .unnest("issues")
        .select(
            "full_name",
            "stargazers_count",
            "comments",
            "created_at",
            "updated_at",
            "labels",
            # pl.col("pull_request").is_null().alias("is_issue")
            )
        # .with_columns(pl.col("labels").list.eval(pl.element().struct.field("name")))
    )

df_all = pl.concat([read_github_json(f) for f in filenames])

df_scatter = df_all.group_by("full_name").agg(
    pl.col("stargazers_count").first(),
    pl.col("comments").sum()
)

df_scatter.plot.scatter(x="stargazers_count", y="comments", color="full_name")


df_ansible = (
    read_github_json("data/github_repos/ansible_ansible.json")
    .with_columns(pl.col("labels").list.eval(pl.element().struct.field("name")))
)

df_label_comments = df_ansible.explode("labels").group_by("full_name", "labels").agg(pl.col("comments").sum())
