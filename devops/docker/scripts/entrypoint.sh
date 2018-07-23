#!/bin/bash

function log() {
    echo [TIMING $(date +"%F %R:%S")] "$@"
}

function trace() {
    [[ -n "${APP_DEBUG}" ]] && log "$@"
}

trapHandler() {
  trace "Stopping nginx"
  /etc/init.d/nginx stop || true

  for PID in ${KILL_LIST[@]}; do
      trace "Killing pid ${PID}"
    kill ${PID}
    wait ${PID}
  done

  trace "Exit"
  exit ${RESULT:-0}
}

function waitForTermination() {
    # Wait for a terminate signal or for the app to stop
    trace "Entering wait loop"
    
    while true
    do
      tail -f /dev/null & wait ${!}
    done
}

function exportAZ() {
    if [[ -n ${AMAZON_METADATA_INSTANCE} ]]; then
        export AMAZON_CURRENT_AZ=$(wget -q -O - "http://${AMAZON_METADATA_INSTANCE}/latest/meta-data/placement/availability-zone")
    fi
    export AMAZON_CURRENT_AZ=${AMAZON_CURRENT_AZ:-local}
    trace "Current AZ is ${AMAZON_CURRENT_AZ}"
}

function main() {
    if [[ -n "${APP_DEBUG}" ]]; then set ${APP_DEBUG}; fi
    trap trapHandler EXIT SIGTERM SIGKILL SIGINT SIGHUP

    trace "Container starting"

    # Switch to the code
    cd /app
    
    # Ensure no extraneous environment files
    rm -f .env*

    # Get the AZ
    exportAZ
    
    # List of processes to kill on termination
    KILL_LIST=()

    # Platform setup
    export PYTHONPATH="/app;${PYTHONPATH}"
    export C_FORCE_ROOT="true"

    # Select way we want to run the app - default is "WEB"
    APP_RUN_MODE="${APP_RUN_MODE:-WEB}"
    trace "Starting in ${APP_RUN_MODE} mode"
    case "${APP_RUN_MODE}" in
        TASK)
            # Run one off tasks, each separated by ";"
            if [[ -n "${APP_TASK_LIST}" ]]; then
                IFS=';' read -ra CMDS <<< "${APP_TASK_LIST}"
                for CMD in "${CMDS[@]}"; do
                    log "Starting task \"python manage.py ${CMD}\""
                    python manage.py ${CMD}
                    RESULT=$? && [[ "${RESULT}" -ne 0 ]] && exit
                done
            fi
            trace "Tasks completed"
            exit
        ;;
        *)
            ENTRYPOINT_SCRIPT="./entrypoint-${APP_RUN_MODE,,}.sh"
            if [[ -f "${ENTRYPOINT_SCRIPT}" ]]; then
                ${ENTRYPOINT_SCRIPT} "$@"
                KILL_LIST+=($!)
            else
                log "ERROR: entrypoint script missing for ${APP_RUN_MODE} mode"
                RESULT=2 && exit
            fi
        ;;
    esac

    # Run forever (hopefully)
    waitForTermination
}

# Away we go
main "$@"


