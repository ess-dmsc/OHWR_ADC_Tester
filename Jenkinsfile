project = "ohwr_adc_tester"

fedora = 'essdmscdm/fedora-build-node:0.3.0'

container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

node("docker") {
    cleanWs()
    dir("${project}") {
        stage("Checkout") {
            scm_vars = checkout scm
        }
    }
    try {
        image = docker.image(fedora)
            container = image.run("\
                --name ${container_name} \
                --tty \
                --network=host \
                --env http_proxy=${env.http_proxy} \
                --env https_proxy=${env.https_proxy} \
            ")
        sh "docker cp ${project} ${container_name}:/home/jenkins/${project}"
        
        stage("Create virtualenv") {
            sh """docker exec ${container_name} bash -c \"
                cd ${project}
                python3.5 -m venv build_env
            \""""
        }
        
        stage("Install requirements") {
            sh """docker exec ${container_name} bash -c \"
                cd ${project}
                build_env/bin/pip install --upgrade pip
                build_env/bin/pip install -r requirements.txt
            \""""
        }
        
        stage("Create package") {
            sh """docker exec ${container_name} bash -c \"
                cd ${project}
                build_env/bin/pyinstaller -w OHWR_ADC_Tester.py
            \""""
        }
        
        stage("Archive package") {
            sh """docker exec ${container_name} bash -c \"
                cd ${project}
                tar czvf OHWR_ADC_Tester.tar.gz -C dist/ OHWR_ADC_Tester/
            \""""
        }
    } finally {
        container.stop()
    }
}