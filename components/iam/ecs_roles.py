import pulumi
import pulumi_aws as aws
from typing import Optional, Dict
import json


class EcsRoles(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        tags: Optional[Dict[str, str]] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__("custom:iam:EcsRoles", name, None, opts)

        # ECS Task Execution Role - for pulling images and writing logs
        execution_role = aws.iam.Role(
            f"{name}-execution-role",
            assume_role_policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }]
            }),
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Attach the AWS managed policy for ECS task execution
        aws.iam.RolePolicyAttachment(
            f"{name}-execution-role-policy",
            role=execution_role.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
            opts=pulumi.ResourceOptions(parent=self)
        )

        # ECS Task Role - for the application to access AWS services
        task_role = aws.iam.Role(
            f"{name}-task-role",
            assume_role_policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }]
            }),
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.execution_role_arn = execution_role.arn
        self.task_role_arn = task_role.arn

        self.register_outputs({
            "execution_role_arn": self.execution_role_arn,
            "task_role_arn": self.task_role_arn
        })

