SELECT
    SELLER_ID,
    SELLER_ZIP_CODE_PREFIX,
    SELLER_CITY,
    SELLER_STATE
FROM {{ source('olist_raw', 'raw_sellers') }}
