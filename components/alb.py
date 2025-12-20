import pulumi
from pulumi_aws import aws 
from pydantic import BaseModel
from typing import Dict ,Optional

class AlbArgs(BaseModel):
    vpc_id:str
    public_subnets:Optional[list]
    tags:Optional[Dict[str ,str]]
    alb_sg:str



class Alb(pulumi.ComponentResource):
    def __init__(self,name ,args:AlbArgs ,opts=None):
        super().__init__("custom:alb:Alb" ,name , None ,opts)
        

        #ALB creation
        self.alb =aws.lb.LoadBalancer(
            f"{name}-alb",
            subnets=args.public_subnets,
            security_groups=[args.alb_sg],
            load_blancer_type="application",
            tags=args.tags,
            opts=pulumi.ResourceOptions(parent=self)
        )
       
       #target group for ALB
        self.target_group=aws.lb.TargetGroup(
            f"{name}-alb-target-group",
            port=8000,
            protocol="HTTP",
            target_type="ip",
            vpc_id=args.vpc_id,
            health_check={
                "path":"/health",
            }
            opts=pulumi.ResourceOptions(parent=self)
        )

        #listener for ALB
        self.listener=aws.lb.Listener(
            f"{name}-alb-listener",
            load_balancer_arn=self.alb.arn,
            port=80,
            protocol="HTTP",
            default_actions=[{
                "type":"forward",
                "target_group_arn":self.target_group.arn
            }],
            opts=pulumi.ResourceOptions(parent=self)
        )
      

        self.register_outputs({
            "alb_arn":self.alb.arn,
            "alb_dns":self.alb.dns_name,
            "target_group_arn":self.target_group.arn,
        })
        