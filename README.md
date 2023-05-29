# Sustainable Product Search Chatgpt Plugin

This is a plugin for the [OpenAI Chat](https://chat.openai.com) platform. It allows users to search for sustainable products and get recommendations based on their preferences.

## Setup

To install the required packages for this plugin, run the following command:

```bash
make deps
```

To run the OpenSearch instance that return product results depending on the user's input, run the following command:

```bash
make run-opensearch
```

Indexing the products in OpenSearch is done by running the following command:

```bash
make index-products
```

To run the plugin, enter the following command:

```bash
make run
```

Once the local server is running:

1. Navigate to https://chat.openai.com.
2. In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).
3. Select "Plugin store"
4. Select "Develop your own plugin"
5. Enter in `localhost:5003` since this is the URL the server is running on locally, then select "Find manifest file".

The plugin should now be installed and enabled! You can start with a question like "Help me find some sustainable shoes"!