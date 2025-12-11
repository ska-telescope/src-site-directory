import io
import json
import os
import pathlib
import tempfile
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi_versionizer.versionizer import api_version
from plantuml import PlantUML
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.exceptions import SchemaNotFound, handle_exceptions
from ska_src_site_capabilities_api.common.utility import load_and_dereference_schema
from ska_src_site_capabilities_api.rest.dependencies import Common

schemas_router = APIRouter()
config = Config(".env")


@api_version(1)
@schemas_router.get(
    "/schemas",
    responses={
        200: {"model": models.response.SchemasListResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Schemas"],
    summary="List schemas",
)
@handle_exceptions
async def list_schemas(request: Request) -> JSONResponse:
    """Get a list of schema names used to define entities."""
    schema_basenames = sorted(["".join(fi.split(".")[:-1]) for fi in os.listdir(config.get("SCHEMAS_RELPATH"))])
    return JSONResponse(schema_basenames)


@api_version(1)
@schemas_router.get(
    "/schemas/{schema}",
    responses={
        200: {"model": models.response.SchemaGetResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Schemas"],
    summary="Get schema",
)
@handle_exceptions
async def get_schema(request: Request, schema: str = Path(description="Schema name")) -> Union[JSONResponse, HTTPException]:
    """Get a schema by name."""
    try:
        dereferenced_schema = load_and_dereference_schema(
            schema_path=pathlib.Path("{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), schema))).absolute()
        )
        return JSONResponse(dereferenced_schema)  # some issue with jsonref return != dict
    except FileNotFoundError:
        raise SchemaNotFound


@api_version(1)
@schemas_router.get(
    "/schemas/render/{schema}",
    responses={
        200: {},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Schemas"],
    summary="Render a schema",
)
@handle_exceptions
async def render_schema(request: Request, schema: str = Path(description="Schema name")) -> Union[JSONResponse, HTTPException]:
    """Render a schema by name."""
    try:
        dereferenced_schema = load_and_dereference_schema(
            schema_path=pathlib.Path("{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), schema))).absolute()
        )
    except FileNotFoundError:
        raise SchemaNotFound

    # pop countries enum for readability
    dereferenced_schema.get("properties").get("sites", {}).get("items", {}).get("properties", {}).get("country", {}).pop("enum", None)

    plantuml = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as schema_file:
        schema_file.write("@startjson\n{}\n@endjson\n".format(json.dumps(dereferenced_schema, indent=2)))
        schema_file.flush()

        image_temp_file_descriptor, image_temp_file_name = tempfile.mkstemp()
        plantuml.processes_file(filename=schema_file.name, outfile=image_temp_file_name)
        with open(image_temp_file_name, "rb") as image_temp_file:
            png = image_temp_file.read()
        os.close(image_temp_file_descriptor)

    return StreamingResponse(io.BytesIO(png), media_type="image/png")
