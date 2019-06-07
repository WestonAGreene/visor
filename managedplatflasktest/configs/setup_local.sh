# All of my understanding of this script was copied from examples in the Sys Scale repo. Examples most prominently used:
# https://REDACTED.redhat.com/REDACTED/REDACTED/blob/master/src/com/redhat/mktg_ops/pipeline/BuildApp.groovy


# echo $PAAS_DEV_URI
# oc login $PAAS_DEV_URI --token $PAAS_DEV_TOKEN_WGREENE --insecure-skip-tls-verify
# oc login https://manage.us-west.dc.preprod.paas.redhat.com:000 --token=WxxJmfijJJ7of_wJliN7Ek87HpdVwjzxCfaDmeVGJS4
oc whoami

APP_NAME=managedplatflasktest
APP_DESCRIPTION=("Testing images")  # must be passed as an array because the qoutation marks were not being recognized and each word was being treated as a new argument
OPENSHIFT_NAMESPACE=visor
REPO_BRANCH=develop
REPO_USER=wgreene
REPO_PASSWORD=$GITLAB_CORP_TOKEN
REPO_URI=$GITLAB_CORP_URI
TEMPLATE_TRIGGERED_BY=wgreene

oc project $OPENSHIFT_NAMESPACE

if [[ $1 == "build" ]]
then
    # oc get all --selector app=$APP_NAME -o name
    # oc delete bc,secret -l app=$APP_NAME  # not necessaryr since the template is being applied

    oc process \
    -f ../../cicd/image_build.yaml \
    -p=APP_NAME=$APP_NAME \
    -p=APP_DESCRIPTION="${APP_DESCRIPTION[@]}" \
    -p=OPENSHIFT_NAMESPACE=$OPENSHIFT_NAMESPACE \
    -p=REPO_BRANCH=$REPO_BRANCH \
    -p=REPO_URI=$REPO_URI \
    -p=REPO_USER=$REPO_USER \
    -p=REPO_PASSWORD=$REPO_PASSWORD \
    -p=TEMPLATE_TRIGGERED_BY=$TEMPLATE_TRIGGERED_BY \
    | oc apply -f -

    oc start-build $APP_NAME

elif [[ $1 == "deploy" ]]
then
    # oc get all --selector app=$APP_NAME -o name
    # oc delete dc,service,route -l app=$APP_NAME

    oc process \
    -f ../../cicd/image_deploy_s2i.yaml \
    -p=APP_NAME=$APP_NAME \
    -p=APP_DESCRIPTION="${APP_DESCRIPTION[@]}" \
    -p=OPENSHIFT_NAMESPACE=$OPENSHIFT_NAMESPACE \
    -p=REPO_BRANCH=$REPO_BRANCH \
    -p=TEMPLATE_TRIGGERED_BY=$TEMPLATE_TRIGGERED_BY \
    | oc apply -f -

else
    echo "You didn't indicate whether to build or deploy the image."
fi
