1. Create the docker image using the following command
```docker build -t sanity-runner-proto-colab .```

2. To Run with Proto Schema

2.1. Move the .pb file to the root folder.
2.2. Open 'docker_orchestrator_proto.ipynb' file and update proto_file_name in 'Parse Proto' section i.e. `proto_file_name = 'tool_use_metadata_set_v2.pb'`

2.3. Run All Cell.

