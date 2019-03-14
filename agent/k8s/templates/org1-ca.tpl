apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  namespace: {{clusterName}}
  name: ca-org1
spec:
  replicas: 1
  strategy: {}
  template:
    metadata:
      labels:
       app: hyperledger
       role: ca
       org: org1
       name: ca
    spec:
     containers:
       - name: ca
         image: hyperledger/fabric-ca:x86_64-1.0.5
         env:
         - name:  FABRIC_CA_HOME
           value: /etc/hyperledger/fabric-ca-server
         - name:  FABRIC_CA_SERVER_CA_NAME
           value: ca
         - name:  FABRIC_CA_SERVER_TLS_ENABLED
           value: "true"
         - name:  FABRIC_CA_SERVER_TLS_CERTFILE
           value: /etc/hyperledger/fabric-ca-server-config/ca.org1.example.com-cert.pem
         - name:  FABRIC_CA_SERVER_TLS_KEYFILE
           value: /etc/hyperledger/fabric-ca-server-config/0e729224e8b3f31784c8a93c5b8ef6f4c1c91d9e6e577c45c33163609fe40011_sk
         ports:
          - containerPort: 7054
         command: ["sh"]
         args:  ["-c", " fabric-ca-server start --ca.certfile /etc/hyperledger/fabric-ca-server-config/ca.org1.example.com-cert.pem --ca.keyfile /etc/hyperledger/fabric-ca-server-config/0e729224e8b3f31784c8a93c5b8ef6f4c1c91d9e6e577c45c33163609fe40011_sk -b admin:adminpw -d "]
         volumeMounts:
          - mountPath: /etc/hyperledger/fabric-ca-server-config
            name: certificate
            subPath: ca/
          - mountPath: /etc/hyperledger/fabric-ca-server
            name: certificate
            subPath: fabric-ca-server/
     volumes:
       - name: certificate
         persistentVolumeClaim:
             claimName: {{clusterName}}-org1-pvc

---
apiVersion: v1
kind: Service
metadata:
   namespace: {{clusterName}}
   name: ca-org1
spec:
 selector:
   app: hyperledger
   role: ca
   org: org1
   name: ca
 type: NodePort
 ports:
   - name: endpoint
     protocol: TCP
     port: 7054
     targetPort: 7054
     nodePort: {{nodePort}}
