set -e

SPARK_SUBMIT="bin/spark-submit"
APP_NAME=""
SCRIPT="template.py"

export PYTHONIOENCODING="utf8"

export SPARK_HOME="/data/opt/spark-2"


${SPARK_HOME}/${SPARK_SUBMIT} \
  --driver-java-options "-Djava.net.preferIPv4Stack=true" \
  --master yarn \
  --name "${APP_NAME}" \
  --conf "spark.app.name=${APP_NAME}" \
  ${SCRIPT}
