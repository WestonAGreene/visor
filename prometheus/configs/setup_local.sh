# All of my understanding of this script was copied from examples in the Sys Scale repo. Examples most prominently used:
# https://REDACTED.redhat.com/REDACTED/REDACTED/blob/master/src/com/redhat/mktg_ops/pipeline/BuildApp.groovy

# TEMPLATE_TRIGGERED_BY=wgreene
APP_NAME=prometheus
BRANCH=develop

if [[ $1 == "build" ]]
then
    oc process \
    -f image_build.yaml \
    -p=APP_NAME=$APP_NAME \
    -p=BRANCH=$BRANCH \
    | oc apply -f -

    oc start-build $APP_NAME-proxy
    # oc start-build $APP_NAME-nginx

elif [[ $1 == "deploy" ]]
then
    oc process \
    -f deploy.yaml \
    -p=APP_NAME=$APP_NAME \
    -p=BRANCH=$BRANCH \
    | oc apply -f -

else
    echo "You didn't indicate whether to build or deploy the image."
fi
