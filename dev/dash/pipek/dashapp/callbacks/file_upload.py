import dash
import json
import base64
import datetime
import pathlib
import io
import time
from dash import html, dash_table

from flask import current_app

from pipek import models
from pipek.web import redis_rq
from pipek.jobs import face_detections


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)

    image_dir_path = pathlib.Path(current_app.config.get("PIPEK_DATA")) / "images"

    image_object = io.BytesIO(decoded)

    stored_filename = f"{image_dir_path}/{filename}"
    stored_path = pathlib.Path(stored_filename)
    while stored_path.exists():
        stored_filename = f"{image_dir_path}/{round(time.time() * 1000)}-{filename}"
        stored_path = pathlib.Path(stored_filename)

    with open(stored_filename, "wb") as f:
        f.write(image_object.getbuffer())

    image = models.Image(
        path=stored_filename,
        filename=filename,
    )

    models.db.session.add(image)
    models.db.session.commit()
    models.db.session.refresh(image)

    job = redis_rq.redis_queue.queue.enqueue(
        face_detections.detect,
        args=(image.id,),
        # job_id=f"",
        timeout=600,
        job_timeout=600,
    )

    return image.id, html.Div(f"{image.id} Upload Completed")


@dash.callback(
    dash.Output("upload-status", "children"),
    dash.Output("upload-image-ids", "children"),
    dash.Output("image-ids", "data"),
    dash.Input("upload-data", "contents"),
    dash.State("upload-data", "filename"),
    dash.State("upload-data", "last_modified"),
)
def upload_image(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is None:
        return "", "", ""

    children = []
    image_ids = []
    for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
        image_id, result = parse_contents(c, n, d)
        children.append(result)
        image_ids.append(image_id)

    return children, html.Div(image_ids), json.dumps(image_ids)


@dash.callback(
    dash.Output("image-results", "children"),
    dash.Input("image-result-interval", "n_intervals"),
    dash.Input("image-ids", "data"),
)
def get_image_results(n_intervals, image_ids):
    if not image_ids:
        return "Not Upload"

    datas = json.loads(image_ids)

    results = dict()
    for image_id in datas:
        print(image_id)
        image = models.db.session.get(models.Image, image_id)
        models.db.session.commit()

        results[image.id] = dict(
            status=image.status, result=image.results, updated_date=image.updated_date
        )

    return html.Div(str(results))
