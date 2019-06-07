## 2017-06-15
- Use 1 replica for PROD Prometheus
  + for HA will have to use separate deployments

## 2017-06-14
- Initial rollout to PROD environment

## 2018-02-19 05:30
 - removed livness probs from the Prometheus dev Open PaaS project as I suspect the probes are killing the pods prematurely

Health check yaml
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /
              port: 9090
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
