project = "ohwr_adc_tester"

centos = 'essdmscdm/centos.python-build-node:0.1.2'

container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

node("docker") {
    cleanWs()
    dir("${project}") {
        stage("Checkout") {
            scm_vars = checkout scm
        }
    }
    try {
        image = docker.image(centos)
            container = image.run("\
                --name ${container_name} \
                --tty \
                --network=host \
                --env http_proxy=${env.http_proxy} \
                --env https_proxy=${env.https_proxy} \
            ")
        sh "docker cp ${project} ${container_name}:/home/jenkins/${project}"
        sh """docker exec --user root ${container_name} bash -e -c \"
            chown -R jenkins.jenkins /home/jenkins/${project}
        \""""

        stage("Create virtualenv") {
            sh """docker exec ${container_name} bash -e -c \"
                cd ${project}
                python3.6 -m venv build_env
            \""""
        }

        stage("Install requirements") {
            sh """docker exec ${container_name} bash -e -c \"
                cd ${project}
                build_env/bin/pip --proxy ${http_proxy} install --upgrade pip
                build_env/bin/pip --proxy ${http_proxy} install -r requirements.txt
            \""""
        }

        stage("Build C++ code") {
            sh """docker exec ${container_name} bash -e -c \"
                cd ${project}
                cmake3 cpp_src -DCMAKE_BUILD_TYPE=Release
                make
            \""""
        }

        stage("Create package") {
            sh """docker exec ${container_name} bash -e -c \"
                cd ${project}
                build_env/bin/pyinstaller -w OHWR_ADC_Tester.py
            \""""
        }

        stage("Archive package") {
            sh """docker exec ${container_name} bash -e -c \"
                cd ${project}
                tar czvf OHWR_ADC_Tester.tar.gz -C dist/ OHWR_ADC_Tester/
            \""""
            sh "docker cp ${container_name}:/home/jenkins/${project}/OHWR_ADC_Tester.tar.gz ."
            archiveArtifacts "OHWR_ADC_Tester.tar.gz,GIT_COMMIT"
        }
    } finally {
        container.stop()
    }
}
