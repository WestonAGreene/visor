# All of my understanding of this script was copied from examples in the Sys Scale repo. Examples most prominently used:
# https://REDACTED.redhat.com/REDACTED/REDACTED/blob/master/src/com/redhat/mktg_ops/pipeline/BuildApp.groovy


# echo $PAAS_DEV_URI
# oc login $PAAS_DEV_URI --token $PAAS_DEV_TOKEN_WGREENE --insecure-skip-tls-verify
# oc login https://manage.us-west.dc.preprod.paas.redhat.com:000 --token=WxxJmfijJJ7of_wJliN7Ek87HpdVwjzxCfaDmeVGJS4

# chmod +x setup_local.sh

oc whoami

APP_NAME=monitor
BRANCH=develop

oc project visor

if [[ $1 == "build" ]]
then
    oc process \
    -f image_build.yaml \
    -p=APP_NAME=$APP_NAME \
    -p=BRANCH=$BRANCH \
    | oc apply -f -

    oc start-build $APP_NAME

elif [[ $1 == "deploy" ]]
then
    oc process \
    -f deploy.yaml \
    -p=BRANCH=$BRANCH \
    -p=APP_NAME=$APP_NAME \
    | oc apply -f -

else
    echo "You didn't indicate whether to build or deploy the image."
fi
