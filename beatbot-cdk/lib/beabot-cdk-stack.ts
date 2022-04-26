import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class BeabotCdkStack extends Stack {
  ecsService: ecs.Ec2Service;
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here
    const vpc = new ec2.Vpc(this, 'VPC');

    const cluster = new ecs.Cluster(this, 'Cluster', {
      vpc,
    });

    cluster.addCapacity('DefaultAutoScalingGroupCapacity', {
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3A, ec2.InstanceSize.SMALL),
      desiredCapacity: 1,
    });

    const taskDefinition = new ecs.Ec2TaskDefinition(this, 'TaskDef');

    taskDefinition.addContainer('DefaultContainer', {
      image: ecs.ContainerImage.fromAsset('../beatbot-code'),
      memoryLimitMiB: 1536,
    });

    this.ecsService = new ecs.Ec2Service(this, 'Service', {
      cluster,
      taskDefinition,
    });
  }
}
