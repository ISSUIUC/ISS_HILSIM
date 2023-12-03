import SwaggerUI from "swagger-ui-react"
import "swagger-ui-react/swagger-ui.css"
import { api_url } from '../dev_config';

function SwaggerUIPage() {
    var openapi_url = api_url + "/api/openapi.json";
 return <SwaggerUI url={openapi_url} />
}

export default SwaggerUIPage;
