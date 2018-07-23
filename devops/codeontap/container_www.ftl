[#case "{containerid}"]
    [#switch containerListMode]
        [#case "definition"]
            [#switch containerListTarget]
                [#case "docker"]
                    [@containerBasicAttributes containerName /]
                    [#break]

                [#case "lambda"]
                    [#break]
            [/#switch]
            [#break]

        [#case "environmentCount"]
        [#case "environment"]
            [@standardEnvironmentVariables
                containerListTarget containerListMode /]
                
            [#switch containerRunMode]
                [#case "WEB"]
                    [@environmentVariable
                        "APP_WORKER_COUNT" "3"
                        containerListTarget containerListMode /]
                    [#break]
                [#case "WORKER"]
                    [@environmentVariable
                        "APP_WORKER_COUNT" "4"
                        containerListTarget containerListMode /]
                    [#break]
            [/#switch]

            [#assign secretKeyDetails =
                        (credentialsObject[formatComponentShortName(
                                            tier,
                                            component,
                                            "${containerid}")])!""]
            [#if secretKeyDetails?has_content]
                [@environmentVariable
                    "DJANGO_SECRET_KEY" secretKeyDetails.API.SecretKey
                    containerListTarget containerListMode /]
            [/#if]
            [#if appSettingsObject.Debug??]
                [@environmentVariable
                    "DJANGO_DEBUG" appSettingsObject.Debug?c
                    containerListTarget containerListMode /]
            [/#if]

            [@environmentVariable
                "DJANGO_TIMEZONE" "Australia/Canberra"
                containerListTarget containerListMode /]

            [#assign dbTier = getTier("db")]
            [#assign dbComponent = getComponent("db", "${containerid}", "rds")]
            [#assign rdsId = formatRDSId(dbTier, dbComponent)]
            [#if getKey(formatRDSDnsId(rdsId))?has_content]
                [@environmentVariable
                    "DATABASE_HOST" getKey(formatRDSDnsId(rdsId))
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "DATABASE_PORT" getKey(formatRDSPortId(rdsId))
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "DATABASE_NAME" getKey(formatRDSDatabaseNameId(rdsId))
                    containerListTarget containerListMode /]
    
                [#assign rdsCredentials = 
                            credentialsObject[formatComponentShortName(
                                                dbTier,
                                                dbComponent)]]

                [@environmentVariable
                    "DATABASE_USERNAME" rdsCredentials.Login.Username                
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "DATABASE_PASSWORD" rdsCredentials.Login.Password
                    containerListTarget containerListMode /]
            [/#if]

            [@environmentVariable
                "RABBITMQ_HOST" "rabbit"
                containerListTarget containerListMode /]
            [@environmentVariable
                "RABBITMQ_PORT" "5672"
                containerListTarget containerListMode /]
            [@environmentVariable
                "RABBITMQ_VHOST" "/"
                containerListTarget containerListMode /]
            [@environmentVariable
                "RABBITMQ_USERNAME" "guest"
                containerListTarget containerListMode /]
            [@environmentVariable
                "RABBITMQ_PASSWORD" "guest"
                containerListTarget containerListMode /]

            [#assign cacheComponent = getComponent("db", "${containerid}", "cache")]
            [#assign cacheId = formatCacheId(dbTier, cacheComponent)]
            [#if getKey(formatCacheDnsId(cacheId))?has_content]
                [@environmentVariable
                    "SESSION_REDIS_HOST" getKey(formatCacheDnsId(cacheId))
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "SESSION_REDIS_PORT" getKey(formatCachePortId(cacheId))
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "SESSION_REDIS_DB" "0"
                    containerListTarget containerListMode /]
    
                [@environmentVariable
                    "CACHE_REDIS_HOST" getKey(formatCacheDnsId(cacheId))
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "CACHE_REDIS_PORT" getKey(formatCachePortId(cacheId))
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "CACHE_REDIS_DB" "1"
                    containerListTarget containerListMode /]
            [/#if]

            [#assign couchdbCredentials = 
                        (credentialsObject[formatComponentShortName(
                                            tier,
                                            component,
                                            "couchdb")])!""]
            [#if couchdbCredentials?has_content]
                [@environmentVariable
                    "COUCHDB_USERNAME" couchdbCredentials.Login.Username
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "COUCHDB_PASSWORD" couchdbCredentials.Login.Password
                    containerListTarget containerListMode /]
            [#else]
                [@environmentVariable
                    "COUCHDB_USERNAME" "admin"
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "COUCHDB_PASSWORD" "changeme"
                    containerListTarget containerListMode /]
            [/#if]            

            [#assign sentryDetails =
                        credentialsObject["sentry"]!""]
            [#if sentryDetails??]
                [@environmentVariable
                    "SENTRY_DSN" sentryDetails.API.SecretKey
                    containerListTarget containerListMode /]
            [/#if]
            
            [#assign sesCredentials = 
                            credentialsObject["smtp"]!""]
            [#if sesCredentials?has_content]
                [@environmentVariable
                    "SMTP_HOST" "email-smtp.us-west-2.amazonaws.com"
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "SMTP_PORT" "587"
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "SMTP_USERNAME" sesCredentials.Login.Username
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "SMTP_PASSWORD" sesCredentials.Login.Password
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "SMTP_USE_TLS" "true"
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "SMTP_FROM_EMAIL" "biosecurity@dawr.gosource.com.au"
                    containerListTarget containerListMode /]
            [/#if]

            [#assign anaTier = getTier("ana")]
            [#assign esComponent = getComponent("ana", "es", "es")]
            [#assign esId = formatElasticSearchId(anaTier, esComponent)]
            [#if getKey(formatElasticSearchDnsId(esId))?has_content]
                [@environmentVariable
                    "ANALYTICS_ES_ENDPOINT"
                    "https://" + 
                        getKey(formatElasticSearchDnsId(cacheId)) +
                        ":443"
                    containerListTarget containerListMode /]
                [@environmentVariable
                    "ANALYTICS_ES_INDEX_NAME"
                    "${containerName}"
                    containerListTarget containerListMode /]
            [/#if]

            [#break]

        [#case "policyCount"]
        [#case "policy"]
            [@policyHeader containerListPolicyName containerListPolicyId  containerListRole/]
            [@cmkDecryptStatement formatSegmentCMKArnId() /]
            [@s3AllStatement dataBucket getAppDataFilePrefix() /]
            [@policyFooter /]
            [#break]

    [/#switch]
    [#break]

