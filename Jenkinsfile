library 'berlin-ci-shared@master'

pipeline {
  agent {
    dockerfile {
      filename "Dockerfile"
      args "-v /etc/passwd:/etc/passwd:ro"
      reuseNode true
    }
  }

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '2'))
  }

  stages {
    stage("build") {
      steps {
        sh "python setup.py build"
      }
    }

    stage("package") {
      steps {
        sh "python setup.py sdist"
      }
    }

    stage("deploy") {
      when {
       branch 'master'
      }
      steps {
        withCredentials([usernamePassword(credentialsId: "Artifactory-Upload-Creds", usernameVariable: "USERNAME", passwordVariable: "PASSWORD")]) {
          sh "twine upload --verbose -u $USERNAME -p $PASSWORD --repository-url https://***REMOVED***/artifactory/api/pypi/pypi-local dist/*"
        }
      }
    }
  }
  post {
    success {
      archiveArtifacts 'dist/*'
    }
  }
}
