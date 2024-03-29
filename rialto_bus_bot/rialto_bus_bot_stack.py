import os
from typing import Mapping, Optional

from aws_cdk import (
    Duration,
    Stack,
    aws_apigateway as apigw,
    aws_certificatemanager as acm,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_route53 as route53,
    aws_route53_targets as targets,
)
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct

LAMBDA_ASSET_PATH = "rialto_bus_bot/lambda"
LAMBDA_RUNTIME = _lambda.Runtime.PYTHON_3_9


class RialtoBusBotStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define lambda and lambda layer
        bot_handler = _lambda.Function(
            self,
            "MainHandler",
            code=_lambda.Code.from_asset(LAMBDA_ASSET_PATH),
            handler="bot.handler",
            runtime=LAMBDA_RUNTIME,
            layers=[self.create_common_layer(LAMBDA_ASSET_PATH, LAMBDA_RUNTIME)],
            environment=self.get_lambda_env(["BOT_TIMEZONE", "BOT_TOKEN"]),
            log_retention=logs.RetentionDays.TWO_WEEKS,
            timeout=Duration.seconds(30),
        )

        # Define API Gateway distribution
        api = apigw.LambdaRestApi(
            self,
            "LambdaRestApi",
            handler=bot_handler,
            proxy=False,
            rest_api_name="rialtoBusBotApi",
        )

        # Add resource to receive webhooks by POST method
        tg_webhook_receive = api.root.add_resource("tg-webhook-receive")
        tg_webhook_receive.add_method("POST")

        # Import existing DNS hosted zone for certificate validation
        dns_zone = os.environ["HOSTED_ZONE_NAME"]
        api_address = f"api.{dns_zone}"
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            "ImportedHostedZone",
            hosted_zone_id=os.environ["HOSTED_ZONE_ID"],
            zone_name=dns_zone,
        )
        certificate = acm.DnsValidatedCertificate(
            self,
            "Certificate",
            domain_name=api_address,
            hosted_zone=hosted_zone,
            region="us-east-1",
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

        # Manually set tags (cfn could not set stack tags for certificate)
        self.set_certificate_tags(certificate, self.tags.render_tags())

        # Setup custom domain name to use instead of default https://***.execute-api.***.amazonaws.com
        custom_domain = api.add_domain_name(
            "CustomDomain",
            certificate=certificate,
            domain_name=api_address,
            endpoint_type=apigw.EndpointType.EDGE,
            security_policy=apigw.SecurityPolicy.TLS_1_2,
        )
        route53.ARecord(
            self,
            "CustomDomainAliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.ApiGatewayDomain(custom_domain)),
            record_name=api_address,
        )

    def create_common_layer(self, entry: str, runtime: _lambda.Runtime) -> PythonLayerVersion:
        return PythonLayerVersion(
            self,
            "CommonLayer",
            layer_version_name=f"{self.stack_name}-common-layer",
            entry=entry,
            compatible_runtimes=[runtime],
        )

    def get_lambda_env(self, env_keys: list) -> Optional[Mapping[str, str]]:
        return {k: os.environ[k] for k in env_keys} or None

    def set_certificate_tags(self, cert: acm.Certificate, tags: list) -> None:
        for tag in tags:
            cert.tags.set_tag(key=tag["Key"], value=tag["Value"])
