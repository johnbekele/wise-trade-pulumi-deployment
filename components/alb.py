import pulumi
import pulumi_aws as aws

class Alb(pulumi.ComponentResource):
    def __init__(self, name, vpc_id, public_subnets, alb_sg,tags, opts=None):
        super().__init__("custom:alb:Alb", name, None, opts)

        self.alb = aws.lb.LoadBalancer(
            f"{name}-alb",
            subnets=public_subnets,
            security_groups=[alb_sg],
            load_balancer_type="application",
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.target_group = aws.lb.TargetGroup(
            f"{name}-tg",
            port=8000,
            protocol="HTTP",
            target_type="ip",
            vpc_id=vpc_id,
            health_check={"path": "/health"},
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.listener = aws.lb.Listener(
            f"{name}-listener",
            load_balancer_arn=self.alb.arn,
            port=80,
            default_actions=[{
                "type": "forward",
                "target_group_arn": self.target_group.arn
            }],
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.register_outputs({
            "alb_dns": self.alb.dns_name,
            "target_group_arn": self.target_group.arn
        })
