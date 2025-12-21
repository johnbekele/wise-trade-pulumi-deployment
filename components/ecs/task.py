import pulumi
import pulumi_aws as aws
from typing import Optional
from pydantic import BaseModel
import json



class TaskArgs(BaseModel):
    mongo_uri: Optional[str] = None
    frontend_image: str
    backend_image: str
    execution_role_arn: Optional[str] = None
    cpu: str = "512"
    memory: str = "1024"


class TaskDefinition(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        *,
        args: TaskArgs,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__("custom:ecs:Task", name, None, opts)

        container_definitions = [
            {
                "name": "frontend",
                "image": args.frontend_image,
                "essential": True,
                "portMappings": [
                    {"containerPort": 80, "hostPort": 80}
                ],
            },
            {
                "name": "backend",
                "image": args.backend_image,
                "essential": True,
                "portMappings": [
                    {"containerPort": 8000, "hostPort": 8000}
                ],
                "environment": [
                    {
                        "name": "MONGO_URI",
                        "value": args.mongo_uri,
                    }
                ],
            },
        ]

        self.task_def = aws.ecs.TaskDefinition(
            f"{name}-task",
            family=f"{name}-family",
            cpu=args.cpu,
            memory=args.memory,
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            execution_role_arn=args.execution_role_arn,
            container_definitions=json.dumps(container_definitions),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "task_def_arn": self.task_def.arn
        })
