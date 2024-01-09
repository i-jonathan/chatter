#! /bin/bash

kubectl apply -f deployment.yaml

kubectl apply -f service.yaml

kubectl port-forward service/chatter 8000:8000       

