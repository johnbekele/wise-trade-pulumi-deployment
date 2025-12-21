import pulumi
import pulumi_aws as aws
from pydantic import BaseModel
from typing import Optional



class EcsServiceArgs(BaseModel):
    desired_count: int = 1


class EcsService(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        *,
        cluster_arn,   
        task_def_arn,      
        private_subnets,           
        ecs_sg,                   
        target_group_arn,       
        args: EcsServiceArgs,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__("custom:ecs:Service", name, None, opts)

        self.service = aws.ecs.Service(
            f"{name}-service",
            cluster=cluster_arn,
            task_definition=task_def_arn,
            desired_count=args.desired_count,
            launch_type="FARGATE",
            network_configuration={
                "subnets": private_subnets,
                "security_groups": [ecs_sg],
                "assign_public_ip": False,
            },
            load_balancers=[{
                "target_group_arn": target_group_arn,
                "container_name": "backend",
                "container_port": 8000,
            }],
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "service_name": self.service.name
        })
