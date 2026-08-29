# K3s inference stack on VLLM ROCM image

```
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
.........................................................-=*%@@%%%%+=:..............................
.......................................................*%@@@@@%@@@@@%#+:............................
......................................................*@@%@@%@@@@@@@@@%#-...........................
......................................................#@#*%@@@@@@@@@@@@%%...........................
.......................................................#%**%@@@@@@@@@@@@%=..........................
......................................................:*#**#@%%@@@@@@@@@%=..........................
......................................................*#*****##@@@@@@@@@@%:.........................
.......................................................*#****%@@@@@@@@@@@@#=........................
.......................................................-#**%%@@@@@@@@@@@@@=.........................
.......................................................-*%%@@#%@@@@@@@@@#-..........................
...........................................................:##@@@@@@@@@@-...........................
..........................................................=*%@@@@@@@@@@@@%-.........................
.......................................................-*@@@@@@@@@@@@@@@@@@#........................
............::::::::::::::::::::::::::::::::::::::::::*@@@@@@@@@@@@@@@@@@@@@%:::::::::::............
...........:-----------------------------------------#@@@@@@@@@@@@@@@@@@@@@@@@----------............
....................................................-@@@@@@@@@@@@@@@@@@@@@@@@@=.....................
..........................----------................#@@@@@@@@@@@@@@@@@@@@@@@@@@.....................
.........................:=@@@@@@@@+:..............=@@@@@@@@@@@@@@@@@@@@@@@@@@@.....................
...........:+++++++++======+@@@@@%+===============+@@@@@@@@@@@@@@@@@@@@@@@@@@@@:....................
.............................%@@%:...............+@@@@@@@@@@@@@@@@@@@@@@@@@@@@*=+==+++++:...........
...........:=============+*==%@@%++============+*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*.....................
.............................#@@*............:+#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%==========:...........
.............................%@@*..-+++:::::*@@@@@@@@@@%%@@@@@@@@@@@@@@@@@@@@#......................
............:::.............#@@@@-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#......................
...........:==============+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@++++++@@@@@=...........
..........................%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#.-+++++:=++:...........
.......................+*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#.......................
...................:===@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%:.......................
..................:#*##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%-=##=---:................
...........:===#%%%@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%=...........
...........-****************************************************************************-...........
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
```
## Summary 1.0
This project was one i took on to learn the fundamentals of Kubernetes and also to familiarize myself with vLLM serving over a cluster on the ROCM image. I am using K3s instead of traditional
k8s since my basic needs did not exceed K3s capabilities. Keeping this project on K3s reduced unneccesary complexity in a homelab setting where i am the only user. This setup requires using the
latest amdgpu linux drivers as well as the dedicated rocm/k8s-device-plugin daemonset. I am also utilizing the rocm/k8s-device-labeller to get more detailed GPU statistics. The k8s-device-plugin 
daemonset is the essential piece to advertise GPU resources properly on the cluster. Advertising the GPU this way on top of adding "resources.limits.amd.com/gpu: 1" to the vLLM manifest allows the 
scheduler to only place pods on nodes whom which the device plugin advertises resources.limits.amd.com/gpu: 1.

This stack was built originally using the model Ornith1.5/9B at full precision. The model is interchangeable but would require a rebuild of the docker image after changing the model field in agent.py 
as well as the vLLM manifest.

### Hardware 1.1 
The cluster Consist of two nodes;

-BeachBumHQ/control plane= (Ryzen 3 5300G desktop, 32gb DDR4, running Ubuntu desktop 26.04) 

&&

-beachbumserve/agent= (Ryzen 9 3900x, RX 7900 XTX, 32gb ddr4, running Ubuntu server 26.04).  

I Chose this hardware specifically to target ROCM 7.0 support since speeds and throughput have greatly increased with proper driver support for AMD silicon in the past year. 


### Deployments 1.2
Within the cluster we run 2 deployment manifests scaled to "replicas=1" since this project only requires availability for personal use. vLLM is the first deployment, using the official vLLm-ROCM image. This depl-
oyment runs the model weights and serves the openAI endpoint on ClusterIP port:8000.
The second deployment is a Streamlit docker image that i built locally integrating the agent.py I wrote to make chat history persistent per session and draw the chat logs on the Streamlit web ui.
This image is built on a python base, and reaches vLLm over cluster dns at port:8000 and broadcasts with node port @192.168.x.xxx:31182. 

-The url in my case http://vllm.vllm-rocm.svc.cluster.local:8000/v1/chat/completions.
-Access at http://192.168.x.xxx:31182


### Services & Exposure 1.3
Both of these deployments are exposed by a service. I initially exposed these by a "kubectl expose" command but have now captured them in a manifest through the "--dry-run=client" to allow the repo 
to be rebuilt declaratively without additional commands. My choice in exposing only the Streamlit image to my LAN was a deliberate decision to minimize attack surface only exposing the service that needs to be interacted with,
while its communication with vLLM stays private within the cluster.



## Requirements 2.0
-prerequisites for running this stack

### Initial set up 2.1

```bash
curl -sfL https://get.k3s.io | sh - 
```
-install latest version of k3s on server machine(for this example it was built upon V1.36.x)


```bash
sudo cat /var/lib/rancher/k3s/server/node-token
```
-Get cluster agent token from file

```bash
curl -sfL https://get.k3s.io | K3S_URL=https://<your_server_ip>:6443 K3S_TOKEN=<your_node_token> sh -
```
-install and start k3s on the agent node using the token

### Docker build 
> You must build the docker image prior to moving on in these steps. See my docker build commands and notes below.  
Install docker desktop with your preferred package manager first.
> The included manifests are pointed at my private dockerhub repo and image. Adjust to your use case.
This is to be built on Python3 base; see dockerfile.
> Streamlit manifest reference a regcred file to pull from a private repo, this is to harden security by removing bare credentials from the manifest. Use the commands below to generate your regcred.
```bash
cd ~/<path_to_repo>/streamlit
```
-Enter into the /streamlit directory
```bash
docker login
```
-Login to your docker account
```bash
docker build --platform linux/amd64 -t <your_username>/<your_repo>:v1 .
```
-Build the docker image at your registry. ( I built this image on a apple silicon mac therefore the --platform linux/amd64 flag was required for the target machines, keep this in mind when building your image
and adjust as necessary for your target machine)
```bash
docker push <your_username>/<your_repo>:v1
```
-Push to your docker hub registry to be able to pull back into k3s as a image in the streamlit manifest. 
```bash
kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=<your_username> --docker-password=<your_token> -n vllm-rocm
```
-Create the "regcred" file using your specific docker token to avoid leaking Docker password into the shell.
>after these steps are completed verify your image is available on dockerhub; if True proceed to firewall config.

### Firewall rules 2.2
To use this repo and run my configuration there is some firewall rule additons that must be made. Please see k8s documentation on the reccomended, optional and required ports @:
https://docs.k3s.io/installation/requirements
If you would like to use my port configuration it is as follows:
use:

```bash
sudo ufw status numbered
```
-show current rules in a numbered list 


```bash
sudo ufw allow <rule> 
```
-Allow for each rule respectively.


```bash
sudo ufw delete "numberofrule"
```
-delete any rules added by mistake if needed. 


### Rules list 2.3

--Control Plane--
  
| Port | Proto | From | Purpose |
|---|---|---|---|
| 22 | tcp | `192.168.4.0/24` | SSH |
| 6443 | tcp | Anywhere | k3s API server (agent join) |
| 8472 | udp | Anywhere | flannel VXLAN overlay |
| 10250 | tcp | Anywhere | kubelet |
| — | — | `10.42.0.0/16` | pod network |
| — | — | `10.43.0.0/16` | service network |
| 31182 | tcp | `192.168.4.0/24` | Streamlit NodePort (LAN access) |

--Agent--

| Port | Proto | From | Purpose |
|---|---|---|---|
| 22 | tcp | Anywhere | SSH |
| 8472 | udp | Anywhere | flannel VXLAN |
| 10250 | tcp | Anywhere | kubelet |
| — | — | `10.42.0.0/16` | pod network |
| — | — | `10.43.0.0/16` | service network |

## Run Commands 3.0

### Apply manifests

```bash
kubectl apply -f manifests/
```
-This will create the namespace first from manifests/00-namespace.yaml that this stack lives within and apply all remaining manifests within this directory, replicating my exact setup. 
the GPU device-plugin daemonset (with a nodeSelector modification to keep it off the control-plane iGPU) is included and applied automatically as well.


### After manifests are applied verify with: 

```bash
kubectl get pods -n vllm-rocm
```
-this will return the active pods with their state

```bash
kubectl logs deployments/vllm -n vllm-rocm -f
```
```bash
kubectl logs deployments/streamlit -n vllm-rocm -f 
```
-These commands are to watch the rolling logs as each service comes up




> keep in mind to run any kubectl commands against components of this stack you need to add the -n vllm-rocm to declare which namespace to perform the requested operation in.

> Sudo prefix maybe required when running kubectl commands  depending on your root access. 

> It should be stated that this project is completely human made with the exception of the file kube_vllm-stack-build-doc.md which was generated with claude from my project notes
and description.
