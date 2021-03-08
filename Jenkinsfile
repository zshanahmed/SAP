#!groovy

node {

    try {
        stage 'Checkout'
            checkout scm

        stage 'Test'
            sh 'virtualenv env -p python3.5'
            sh '. env/bin/activate'
            sh 'env/bin/pip install -r requirements.txt'
            sh 'env/bin/python3.5 manage.py test'
    }

    catch (err) {
        sh "echo 'something has gone wrong'"

        throw err
    }

}
