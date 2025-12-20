from typing import Awaitable
import pulumi
from pulumi.output import Inputs
from pulumi_aws import aws 
from pydantic import BaseModel
from typing import Dict ,Optional

class SecurityArgs(BaseModel):
    vpc_id:str
    tags:Optional[Dict[str ,str]]


class SecurityGroups(pulumi.ComponentResource):
    def __init__(self,name ,args:SecurityArgs ,opts=None):
        super().__init__("custome:security:SecurityGroups" ,name , None ,opts)


        #SG for elb

        self.alb_sg=aws.ec2.SecurityGroup(
            f"{name}-alb-security-group",
            vpc_id=args.vpc_id,
            description="allow HTTP internate access",
            ingress=[{
                "protocl":"tcp",
                "from_port":80,
                "to_port":80,
                "cird_blocks":["0.0.0.0/0"]
            }],
            egress=[{
                "protocol":"-1",
                "port":0,
                "to_port":0,
                "cird_blocks":["0.0.0.0/0"]
            }],
            tags=args.tags,
            opts=pulumi.ResourceOptions(parent=self)
        )

        #SG for ECS running fast api
        self.ecs_sg=aws.ec2.SecurityGroup(
            f"{name}-ecs-security-group",
            description="Allow traffic from ALB ",
            ingress=[{
                "protocol":"tcp",
                "from_port":8000,
                "to_port":8000,
                "security_groups":[self.alb_sg.id]
            }],
            egress=[{
                "protocol":"-1",
                "from_port":0,
                "to_port":0,
                "cidr_blocks":["0.0.0.0/0"]
            }],
            tags=args.tags,
            opts=pulumi.ResourceOptions(parent=self)
        )


