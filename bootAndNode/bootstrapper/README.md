Template for Subsystem .sh Files
===============================

Here is a generic template that follows the provided format. This template includes placeholders for the subsystem name and Docker image name, which should be replaced with the specific details for each subsystem.

```
#!/bin/bash

# Placeholder values - replace SUBSYSTEM_NAME and DOCKER_IMAGE_NAME with actual values
SUBSYSTEM_NAME="SUBSYSTEM_NAME"
DOCKER_IMAGE_NAME="DOCKER_IMAGE_NAME"

printf "\n\n"
printf "********************************************************"; \
echo "---------------------- ${SUBSYSTEM_NAME} -------------------------"; \
printf "********************************************************"; \
echo "Deploying ${SUBSYSTEM_NAME}.........."
printf "\n\n"

path="./${SUBSYSTEM_NAME}"
cd ${path}
echo $1 | sudo -S docker build . -t ${DOCKER_IMAGE_NAME}:latest;
echo $1 | sudo -S docker run -d ${DOCKER_IMAGE_NAME}
```


# Initialization File (init.json)

The initialization file specifies the sequence and configuration for each subsystem. It could look something like this:

```
{
    "sequence": [
        "node_manager",
        "security",
        ...
        "workflow_engine"
    ],
    "subsystems": [
        {"name": "node_manager", "script_path": "path/to/node_manager", "dependencies": []},
        {"name": "security", "script_path": "path/to/security", "dependencies": ["node_manager"]},
        ...
        {"name": "workflow_engine", "script_path": "path/to/workflow_engine", "dependencies": ["node_manager", "security"]},
        ...
    ]
}
```

Since the subsystems are dependent on each other, the `dependencies` field is used to specify the order in which the subsystems should be deployed. The `sequence` field specifies the order in which the subsystems should be deployed. The `script_path` field specifies the path to the subsystem's .sh file.