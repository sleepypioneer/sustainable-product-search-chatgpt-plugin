import json
import logging

import quart
import quart_cors
from quart import request
from opensearchpy import OpenSearch

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

INDEX_NAME = "green_products"
host = 'localhost'
port = 9200
auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_compress=True,  # enables gzip compression for request bodies
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)


@app.route('/green-product-search/<string:search_term>', methods=['GET', 'OPTIONS'])
async def green_products_handler(search_term):
    body = {
        "query": {
            "match": {
                "name": {
                    "query": search_term,
                    "fuzziness": 1
                }
            }
        }
    }

    try:
        res = client.search(index='', body=body)
    except Exception as e:
        logging.error("Error: {}".format(e))
        return "Index not found", 404

    return quart.Response(response=json.dumps(res['hits']['hits']), status=200)


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()