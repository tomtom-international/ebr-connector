"""The dynamic template configuration used when creating index templates.
We prefer dynamic templates over fixed ones to avoid updating the Elasticsearch cluster.
"""

DYNAMIC_TEMPLATES = [
    {
        "nested_fields": {
            "match": "br_*_nested",
            "mapping": {
                "type": "nested"
            }
        }
    },
    {
        "count_fields": {
            "match": "br_*_count",
            "mapping": {
                "type": "integer"
            }
        }
    },
    {
        "duration_fields": {
            "match": "br_*duration*",
            "mapping": {
                "type": "float"
            }
        }
    },
    {
        "keyword_only_fields": {
            "match": "br_*_key",
            "match_mapping_type": "string",
            "mapping": {
                "type": "keyword",
                "ignore_above": 256
            }
        }
    },
    {
        "message_field": {
            "mapping": {
                "norms": False,
                "type": "text"
            },
            "match_mapping_type": "string",
            "path_match": "message"
        }
    },
    {
        "string_fields": {
            "mapping": {
                "fields": {
                    "raw": {
                        "ignore_above": 256,
                        "type": "keyword"
                    }
                },
                "norms": False,
                "type": "text"
            },
            "match": "*",
            "match_mapping_type": "string"
        }
    }
]
