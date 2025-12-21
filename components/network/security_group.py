import pulumi
import pulumi_aws as aws

class SecurityGroups(pulumi.ComponentResource):
    def __init__(self, name, vpc_id, opts=None):
        super().__init__("custom:security:SecurityGroups", name, None, opts)

        # ALB SG
        self.alb_sg = aws.ec2.SecurityGroup(
            f"{name}-alb-sg",
            vpc_id=vpc_id,
            description="Allow HTTP from internet",
            ingress=[{
                "protocol": "tcp",
                "from_port": 80,
                "to_port": 80,
                "cidr_blocks": ["0.0.0.0/0"]
            }],
            egress=[{
                "protocol": "-1",
                "from_port": 0,
                "to_port": 0,
                "cidr_blocks": ["0.0.0.0/0"]
            }],
            tags={"Name": f"{name}-alb-sg"},
            opts=pulumi.ResourceOptions(parent=self)
        )

        # ECS SG
        self.ecs_sg = aws.ec2.SecurityGroup(
            f"{name}-ecs-sg",
            vpc_id=vpc_id,
            description="Allow traffic from ALB",
            ingress=[{
                "protocol": "tcp",
                "from_port": 8000,
                "to_port": 8000,
                "security_groups": [self.alb_sg.id]
            }],
            egress=[{
                "protocol": "-1",
                "from_port": 0,
                "to_port": 0,
                "cidr_blocks": ["0.0.0.0/0"]
            }],
            tags={"Name": f"{name}-ecs-sg"},
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.register_outputs({
            "alb_sg": self.alb_sg.id,
            "ecs_sg": self.ecs_sg.id
        })
