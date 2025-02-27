import pyspark.sql.types as T
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pprint import pprint

from py4j.protocol import Py4JJavaError

import json

# "_links": {
#     "self": {
#         "href": "http://api.tvmaze.com/episodes/10897"
#     }
# }

data_dir = "/opt/spark/data"

# ---------------------------------------------------------------- #
# ----------------  Define SCHEMA  ------------------------------- #
# ---------------------------------------------------------------- #
episode_links_schema = T.StructType(
    [
        T.StructField(
            "self",
            T.StructType(
                [
                    T.StructField("href", T.StringType())
                ]
            )
        )
    ]
)

episode_image_schema = T.StructType(
    [
        T.StructField("medium", T.StringType()),
        T.StructField("original", T.StringType()),
    ]
)

episode_schema = T.StructType(
    [
        T.StructField("_links", episode_links_schema),
        T.StructField("airdate", T.DateType()),
        T.StructField("airstamp", T.TimestampType()),
        T.StructField("airtime", T.StringType()),
        T.StructField("id", T.StringType()),
        T.StructField("image", episode_image_schema),
        T.StructField("name", T.StringType()),
        T.StructField("number", T.LongType()),
        T.StructField("runtime", T.LongType()),
        T.StructField("season", T.LongType()),
        T.StructField("summary", T.StringType()),
        T.StructField("url", T.StringType()),
    ]
)
# ---------------------------------------------------------------- #

embedded_schema = T.StructType(
    [T.StructField("episodes", T.ArrayType(episode_schema))]
)

network_schema = T.StructType(
    [
        T.StructField(
            "country",
            T.StructType(
                [
                    T.StructField("code", T.StringType()),
                    T.StructField("name", T.StringType()),
                    T.StructField("timezone", T.StringType()),
                ]
            ),
        ),
        T.StructField("id", T.LongType()),
        T.StructField("name", T.StringType()),
    ]
)

shows_schema = T.StructType(
    [
        T.StructField("_embedded", embedded_schema),
        T.StructField("language", T.StringType()),
        T.StructField("name", T.StringType()),
        T.StructField("network", network_schema),
        T.StructField("officialSite", T.StringType()),
        T.StructField("premiered", T.StringType()),
        T.StructField(
            "rating", T.StructType([T.StructField("average", T.DoubleType())])
        ),
        T.StructField("runtime", T.LongType()),
        T.StructField(
            "schedule",
            T.StructType(
                [
                    T.StructField("days", T.ArrayType(T.StringType())),
                    T.StructField("time", T.StringType()),
                ]
            ),
        ),
        T.StructField("status", T.StringType()),
        T.StructField("summary", T.StringType()),
        T.StructField("type", T.StringType()),
        T.StructField("updated", T.LongType()),
        T.StructField("url", T.StringType()),
        T.StructField("webChannel", T.StringType()),
        T.StructField("weight", T.LongType()),
    ]
)

spark = SparkSession.builder.getOrCreate()

# Always use FAILFAST!
shows_with_schema = spark.read.json(
    f"{data_dir}/shows/shows-silicon-valley.json",
    schema=shows_schema,
    mode="FAILFAST",
)
print('\n ** shows_with_schema ** ')
shows_with_schema.show(5)

# Check for each episode
for column in ["airdate", "airstamp"]:
    (shows_with_schema
        .select(f"_embedded.episodes.{column}")
        .select(F.explode(column).alias(column))
        .show(5))

# poluted schema (intentionally changing two StringType() to LongType())
shows_schema2 = T.StructType(
    [
        T.StructField("_embedded", embedded_schema),
        T.StructField("language", T.StringType()),
        T.StructField("name", T.StringType()),
        T.StructField("network", network_schema),
        T.StructField("officialSite", T.StringType()),
        T.StructField("premiered", T.StringType()),
        T.StructField(
            "rating", T.StructType([T.StructField("average", T.DoubleType())])
        ),
        T.StructField("runtime", T.LongType()),
        T.StructField(
            "schedule",
            T.StructType(
                [
                    T.StructField("days", T.ArrayType(T.StringType())),
                    T.StructField("time", T.StringType()),
                ]
            ),
        ),
        T.StructField("status", T.StringType()),
        T.StructField("summary", T.StringType()),
        T.StructField("type", T.LongType()),  # <2>
        T.StructField("updated", T.LongType()),
        T.StructField("url", T.LongType()),  # <2>
        T.StructField("webChannel", T.StringType()),
        T.StructField("weight", T.LongType()),
    ]
)

shows_with_schema_wrong = spark.read.json(
    f"{data_dir}/shows/shows-silicon-valley.json",
    schema=shows_schema2, mode="FAILFAST",
)



try:
    shows_with_schema_wrong.show()
except Py4JJavaError as ex:
    print('\n ** Error with scheme ** ')
    print(ex.errmsg)
    print('\n')


print('\n ** schedule ** ')
pprint(shows_with_schema.select("schedule").schema.jsonValue())

print('\n ** array_example ** ')
pprint(T.StructField("array_example", T.ArrayType(T.StringType())).jsonValue())

print('\n ** map_example ** ')
pprint(T.StructField("map_example", T.MapType(T.StringType(), T.LongType())).jsonValue())


print('\n ** map_example + array_example ** ')
pprint(
    T.StructType(
        [
            T.StructField("map_example", T.MapType(T.StringType(), T.LongType())),
            T.StructField("array_example", T.ArrayType(T.StringType())),
        ]
    ).jsonValue()
)


other_shows_schema = T.StructType.fromJson(
    json.loads(shows_with_schema.schema.json())
)
