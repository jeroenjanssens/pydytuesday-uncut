import polars as pl
from plotnine import *

# Load the data
origins = pl.read_csv(
    "data/api_origins.csv", null_values=["NA"], infer_schema_length=None
)
info = pl.read_csv("data/api_info.csv", null_values=["NA"], infer_schema_length=None)
categories = pl.read_csv(
    "data/api_categories.csv", null_values=["NA"], infer_schema_length=None
)
apis = pl.read_csv(
    "data/apisguru_apis.csv", null_values=["NA"], infer_schema_length=None
)
logos = pl.read_csv("data/api_logos.csv", null_values=["NA"], infer_schema_length=None)

# Create bar chart
ggplot(origins, aes(x="format")) + geom_bar()

# Duplicates
origins.group_by("name").agg("format").filter(pl.col("format").list.len() > 1)
origins.with_columns(is_duplicated=pl.col("name").is_duplicated()).filter(
    "is_duplicated"
)

# Look at the XCKD logo
logos.filter(pl.col("name").str.contains("xkcd")).item(0, "url")

info_not_null = info.drop_nulls("license_name")

df = info.join(logos, on="name").select(
    "name", "license_name", "url", "background_color"
)

# Aggregate into organization

orgs = (
    df.drop_nulls("license_name")
    .with_columns(org=pl.col("name").str.split(":").list.first())
    .filter(pl.col("url").str.contains_any(["jpg", "jpeg", "png"]))
    .group_by("org")
    .agg(pl.all().unique().first(), count=pl.len())
    .filter(pl.col("count") < 30)
    .sort("count", descending=True)
    .head(10)
)

# Create Great Table

(
    orgs.style.fmt_image("url")
    .cols_hide(["name", "background_color"])
    .cols_move_to_start("url")
    .cols_label(org="Organization", license_name="License", count="#APIs", url="")
    .tab_stub("url")
    # .fmt_nanoplot("count")
    .data_color("count", palette="Greens")
)
