from aws_cdk import (
    core as cdk,
    aws_lambda_python as _lambda,
    aws_apigateway as apigw
)


class RialtoBusBotStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        main_handler = _lambda.PythonFunction(
            self,
            "MainHandler",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset("lambda"),
            handler="bot.handler",
            timeout=10
        )
