"""Tests for Serverless Workflow specification examples."""

from pathlib import Path

import pytest

from serverlessworkflow.sdk.base import (
    Duration,
    Export,
    Input,
    Output,
)
from serverlessworkflow.sdk.call_tasks import (
    AsyncApiMessageConsumptionPolicy,
    AsyncApiOutboundMessage,
    AsyncApiServer,
    AsyncApiSubscription,
    CallAsyncApiArguments,
    CallAsyncApiTask,
    CallFunctionTask,
    CallGrpcArguments,
    CallGrpcTask,
    CallHttpArguments,
    CallHttpTask,
    CallMcpArguments,
    CallMcpTask,
    CallOpenApiArguments,
    CallOpenApiTask,
    GrpcService,
    McpStdioTransport,
    McpTransport,
)
from serverlessworkflow.sdk.tasks import (
    CatchConfiguration,
    ContainerConfiguration,
    ContainerLifetime,
    EmitConfiguration,
    EmitTask,
    ForConfiguration,
    ForkConfiguration,
    ForkTask,
    ForTask,
    ListenConfiguration,
    ListenTask,
    RaiseConfiguration,
    RaiseTask,
    RunConfiguration,
    RunTask,
    ScriptConfiguration,
    SetTask,
    ShellConfiguration,
    SubscriptionIterator,
    SwitchCase,
    SwitchTask,
    TryTask,
    WaitTask,
    WorkflowConfiguration,
)
from serverlessworkflow.sdk.workflow import Document, Schedule, Workflow

SPEC_EXAMPLES_DIR = (
    Path(__file__).parent.parent.parent / "submodules" / "specification" / "examples"
)


@pytest.mark.spec_example
@pytest.mark.parametrize(
    "example_file", list(SPEC_EXAMPLES_DIR.glob("*.yaml")), ids=lambda f: f.name
)
def test_spec_examples(example_file):
    """Test that specification example files can be parsed and serialized correctly."""
    with open(example_file, encoding="utf-8") as f:
        baseline_workflow = Workflow.from_yaml(f.read())

    print(f"Testing workflow from {example_file.name}:")

    match example_file.name:
        case "accumulate-room-readings.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="examples",
                    name="accumulate-room-readings",
                    version="0.1.0",
                ),
                do=[
                    {
                        "consumeReading": ListenTask(
                            listen=ListenConfiguration(
                                to={
                                    "all": [
                                        {
                                            "with": {
                                                "source": "https://my.home.com/sensor",
                                                "type": "my.home.sensors.temperature",
                                            },
                                            "correlate": {"roomId": {"from": ".roomid"}},
                                        },
                                        {
                                            "with": {
                                                "source": "https://my.home.com/sensor",
                                                "type": "my.home.sensors.humidity",
                                            },
                                            "correlate": {"roomId": {"from": ".roomid"}},
                                        },
                                    ]
                                }
                            ),
                            output=Output(as_=".data.reading"),
                        )
                    },
                    {
                        "logReading": ForTask(
                            for_=ForConfiguration(each="reading", in_=".readings"),
                            do=[
                                {
                                    "callOrderService": CallOpenApiTask(
                                        with_=CallOpenApiArguments(
                                            document={
                                                "endpoint": "http://myorg.io/ordersservices.json"
                                            },
                                            operationId="logreading",
                                        )
                                    )
                                }
                            ],
                        )
                    },
                    {
                        "generateReport": CallOpenApiTask(
                            with_=CallOpenApiArguments(
                                document={"endpoint": "http://myorg.io/ordersservices.json"},
                                operationId="produceReport",
                            )
                        )
                    },
                ],
                timeout={"after": {"hours": 1}},
            )
        case "authentication-bearer-uri-format.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="examples",
                    name="bearer-auth",  # Note: filename doesn't match internal name
                    version="0.1.0",
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint={
                                    "uri": "https://petstore.swagger.io/v2/pet/{petId}",
                                    "authentication": {"bearer": {"token": "${ .token }"}},
                                },
                            )
                        )
                    }
                ],
            )
        case "authentication-bearer.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="examples",
                    name="bearer-auth-uri-format",  # Note: filename doesn't match internal name
                    version="0.1.0",
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint={
                                    "uri": "https://petstore.swagger.io/v2/pet/1",
                                    "authentication": {"bearer": {"token": "${ .token }"}},
                                },
                            )
                        )
                    }
                ],
            )
        case "authentication-oauth2-secret.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="oauth2-authentication", version="1.0.0"
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint={
                                    "uri": "https://petstore.swagger.io/v2/pet/{petId}",
                                    "authentication": {"oauth2": {"use": "mySecret"}},
                                },
                            )
                        )
                    }
                ],
                use={"secrets": ["mySecret"]},
            )
        case "authentication-oauth2.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="oauth2-authentication", version="0.1.0"
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint={
                                    "uri": "https://petstore.swagger.io/v2/pet/{petId}",
                                    "authentication": {
                                        "oauth2": {
                                            "authority": "http://keycloak/realms/fake-authority",
                                            "endpoints": {
                                                "token": "/auth/token",
                                                "introspection": "/auth/introspect",
                                            },
                                            "grant": "client_credentials",
                                            "client": {
                                                "id": "workflow-runtime-id",
                                                "secret": "workflow-runtime-secret",
                                            },
                                        }
                                    },
                                },
                            )
                        )
                    }
                ],
            )
        case "authentication-oidc-secret.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="oidc-authentication", version="1.0.0"
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint={
                                    "uri": "https://petstore.swagger.io/v2/pet/{petId}",
                                    "authentication": {"oidc": {"use": "mySecret"}},
                                },
                            )
                        )
                    }
                ],
                use={"secrets": ["mySecret"]},
            )
        case "authentication-oidc.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="oidc-authentication", version="0.1.0"
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint={
                                    "uri": "https://petstore.swagger.io/v2/pet/{petId}",
                                    "authentication": {
                                        "oidc": {
                                            "authority": "http://keycloak/realms/fake-authority",
                                            "grant": "client_credentials",
                                            "client": {
                                                "id": "workflow-runtime-id",
                                                "secret": "workflow-runtime-secret",
                                            },
                                        }
                                    },
                                },
                            )
                        )
                    }
                ],
            )
        case "authentication-reusable.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="bearer-auth", version="0.1.0"
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint={
                                    "uri": "https://petstore.swagger.io/v2/pet/{petId}",
                                    "authentication": {"use": "petStoreAuth"},
                                },
                            )
                        )
                    }
                ],
                use={"authentications": {"petStoreAuth": {"bearer": {"token": "${ .token }"}}}},
            )
        case "call-http-endpoint-interpolation-shorthand.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="examples",
                    name="call-http-shorthand-endpoint",
                    version="0.1.0",
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get", endpoint="https://petstore.swagger.io/v2/pet/{petId}"
                            )
                        )
                    }
                ],
            )
        case "call-http-endpoint-interpolation.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="examples",
                    name="call-http-shorthand-endpoint",
                    version="0.1.0",
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint='${ "https://petstore.swagger.io/v2/pet/\\(.petId)" }',
                                headers={"content-type": "application/json"},
                            )
                        )
                    }
                ],
            )
        case "call-http-query-headers-expressions.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="examples",
                    name="http-query-headers-expressions",
                    version="1.0.0",
                ),
                do=[
                    {
                        "setQueryAndHeaders": SetTask(
                            set={
                                "query": {"search": "${.searchQuery}"},
                                "headers": {"Accept": "application/json"},
                            }
                        )
                    },
                    {
                        "searchStarWarsCharacters": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint="https://swapi.dev/api/people/",
                                headers="${.headers}",
                                query="${.query}",
                            )
                        )
                    },
                ],
                input={
                    "schema": {
                        "format": "json",
                        "document": {
                            "type": "object",
                            "required": ["searchQuery"],
                            "properties": {"searchQuery": {"type": "string"}},
                        },
                    }
                },
            )
        case "call-http-query-parameters.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="http-query-params", version="1.0.0"
                ),
                do=[
                    {
                        "searchStarWarsCharacters": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint="https://swapi.dev/api/people/",
                                query={"search": "${.searchQuery}"},
                            )
                        )
                    }
                ],
                input={
                    "schema": {
                        "format": "json",
                        "document": {
                            "type": "object",
                            "required": ["searchQuery"],
                            "properties": {"searchQuery": {"type": "string"}},
                        },
                    }
                },
            )
        case "call-http-redirect.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="http-query-params", version="1.0.0"
                ),
                do=[
                    {
                        "searchStarWarsCharacters": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint="https://swapi.dev/api/people/",
                                query={"search": "${.searchQuery}"},
                                redirect=True,
                            )
                        )
                    }
                ],
                input={
                    "schema": {
                        "format": "json",
                        "document": {
                            "type": "object",
                            "required": ["searchQuery"],
                            "properties": {"searchQuery": {"type": "string"}},
                        },
                    }
                },
            )
        case "conditional-task.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="default", name="conditional-task", version="0.1.0"
                ),
                do=[
                    {
                        "raiseErrorIfUnderage": RaiseTask(
                            if_=".customer.age < 18",
                            raise_=RaiseConfiguration(
                                error={
                                    "type": "https://superbet-casinos.com/customer/access-forbidden",
                                    "status": 400,
                                    "title": "Access Forbidden",
                                }
                            ),
                            then="end",
                        )
                    },
                    {
                        "placeBet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="post",
                                endpoint="https://superbet-casinos.com/api/bet/on/football",
                                body={"customer": ".customer", "bet": ".bet"},
                            )
                        )
                    },
                ],
            )
        case "fork.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="fork-example", version="0.1.0"
                ),
                do=[
                    {
                        "raiseAlarm": ForkTask(
                            fork=ForkConfiguration(
                                compete=True,
                                branches=[
                                    {
                                        "callNurse": CallHttpTask(
                                            with_=CallHttpArguments(
                                                method="put",
                                                endpoint="https://fake-hospital.com/api/v3/alert/nurses",
                                                body={
                                                    "patientId": "${ .patient.fullName }",
                                                    "room": "${ .room.number }",
                                                },
                                            )
                                        )
                                    },
                                    {
                                        "callDoctor": CallHttpTask(
                                            with_=CallHttpArguments(
                                                method="put",
                                                endpoint="https://fake-hospital.com/api/v3/alert/doctor",
                                                body={
                                                    "patientId": "${ .patient.fullName }",
                                                    "room": "${ .room.number }",
                                                },
                                            )
                                        )
                                    },
                                ],
                            )
                        )
                    }
                ],
            )
        case "for.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="for-example", version="0.1.0"
                ),
                do=[
                    {
                        "checkup": ForTask(
                            for_=ForConfiguration(each="pet", in_=".pets", at="index"),
                            while_=".vet != null",
                            do=[
                                {
                                    "waitForCheckup": ListenTask(
                                        listen=ListenConfiguration(
                                            to={
                                                "one": {
                                                    "with": {
                                                        "type": "com.fake.petclinic.pets.checkup.completed.v2"
                                                    }
                                                }
                                            }
                                        ),
                                        output=Output(as_='.pets + [{ "id": $pet.id }]'),
                                    )
                                }
                            ],
                        )
                    }
                ],
            )
        case "listen-to-one.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="listen-to-one", version="0.1.0"
                ),
                do=[
                    {
                        "waitForStartup": ListenTask(
                            listen=ListenConfiguration(
                                to={
                                    "one": {
                                        "with": {
                                            "type": "com.virtual-wf-powered-race.events.race.started.v1"
                                        }
                                    }
                                }
                            )
                        )
                    },
                    {
                        "startup": CallHttpTask(
                            with_=CallHttpArguments(
                                method="post",
                                endpoint={
                                    "uri": "https://virtual-wf-powered-race.com/api/v4/cars/{carId}/start"
                                },
                            )
                        )
                    },
                ],
            )
        case "raise-inline.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="raise-not-implemented", version="0.1.0"
                ),
                do=[
                    {
                        "notImplemented": RaiseTask(
                            raise_=RaiseConfiguration(
                                error={
                                    "type": "https://serverlessworkflow.io/errors/not-implemented",
                                    "status": 500,
                                    "title": "Not Implemented",
                                    "detail": "${ \"The workflow '\\( $workflow.definition.document.name ):\\( $workflow.definition.document.version )' is a work in progress and cannot be run yet\" }",
                                }
                            )
                        )
                    }
                ],
            )
        case "do-multiple.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="examples",
                    name="call-http-shorthand-endpoint",
                    version="0.1.0",
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get", endpoint="https://petstore.swagger.io/v2/pet/{petId}"
                            )
                        )
                    },
                    {
                        "buyPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="put",
                                endpoint="https://petstore.swagger.io/v2/pet/{petId}",
                                body='${ . + { status: "sold" } }',
                            )
                        )
                    },
                ],
            )
        case "do-single.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="examples",
                    name="call-http-shorthand-endpoint",
                    version="0.1.0",
                ),
                do=[
                    {
                        "getPet": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get", endpoint="https://petstore.swagger.io/v2/pet/{petId}"
                            )
                        )
                    }
                ],
            )
        case "emit.yaml":
            new_workflow = Workflow(
                document=Document(dsl="1.0.2", namespace="test", name="emit", version="0.1.0"),
                do=[
                    {
                        "emitEvent": EmitTask(
                            emit=EmitConfiguration(
                                event={
                                    "with": {
                                        "source": "https://petstore.com",
                                        "type": "com.petstore.order.placed.v1",
                                        "data": {
                                            "client": {
                                                "firstName": "Cruella",
                                                "lastName": "de Vil",
                                            },
                                            "items": [{"breed": "dalmatian", "quantity": 101}],
                                        },
                                    }
                                }
                            )
                        )
                    }
                ],
            )
        case "set.yaml":
            new_workflow = Workflow(
                document=Document(dsl="1.0.2", namespace="test", name="set", version="0.1.0"),
                do=[{"initialize": SetTask(set={"startEvent": "${ $workflow.input[0] }"})}],
                schedule={
                    "on": {
                        "one": {"with": {"type": "io.serverlessworkflow.samples.events.trigger.v1"}}
                    }
                },
            )
        case "set-expression.yaml":
            new_workflow = Workflow(
                document=Document(dsl="1.0.2", namespace="test", name="set", version="0.1.0"),
                do=[{"initialize": SetTask(set="${ $workflow.input[0] }")}],
                schedule={
                    "on": {
                        "one": {"with": {"type": "io.serverlessworkflow.samples.events.trigger.v1"}}
                    }
                },
            )
        case "wait-duration-inline.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="wait-duration-inline", version="0.1.0"
                ),
                do=[{"wait30Seconds": WaitTask(wait=Duration(seconds=30))}],
            )
        case "wait-duration-iso8601.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="wait-duration-8601", version="0.1.0"
                ),
                do=[{"wait30Seconds": WaitTask(wait="PT30S")}],
            )
        case "call-asyncapi-publish.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="bearer-auth", version="0.1.0"
                ),
                do=[
                    {
                        "findPet": CallAsyncApiTask(
                            with_=CallAsyncApiArguments(
                                document={"endpoint": "https://fake.com/docs/asyncapi.json"},
                                operation="findPetsByStatus",
                                server=AsyncApiServer(name="staging"),
                                message=AsyncApiOutboundMessage(payload={"petId": "${ .pet.id }"}),
                                authentication={"bearer": {"token": "${ .token }"}},
                            )
                        )
                    }
                ],
            )
        case "call-asyncapi-subscribe-consume-amount.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="bearer-auth", version="0.1.0"
                ),
                do=[
                    {
                        "getNotifications": CallAsyncApiTask(
                            with_=CallAsyncApiArguments(
                                document={"endpoint": "https://fake.com/docs/asyncapi.json"},
                                operation="getNotifications",
                                protocol="ws",
                                subscription=AsyncApiSubscription(
                                    filter="${ .correlationId == $context.userId and .payload.from.firstName == $context.contact.firstName and .payload.from.lastName == $context.contact.lastName }",
                                    consume=AsyncApiMessageConsumptionPolicy(amount=5),
                                ),
                            )
                        )
                    }
                ],
            )
        case "call-asyncapi-subscribe-consume-forever-foreach.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="bearer-auth", version="0.1.0"
                ),
                do=[
                    {
                        "getNotifications": CallAsyncApiTask(
                            with_=CallAsyncApiArguments(
                                document={"endpoint": "https://fake.com/docs/asyncapi.json"},
                                operation="getNotifications",
                                subscription=AsyncApiSubscription(
                                    filter="${ .correlationId == $context.userId and .payload.from.firstName == $context.contact.firstName and .payload.from.lastName == $context.contact.lastName }",
                                    consume=AsyncApiMessageConsumptionPolicy(while_="${ true }"),
                                    foreach=SubscriptionIterator(
                                        item="message",
                                        do=[
                                            {
                                                "publishCloudEvent": EmitTask(
                                                    emit=EmitConfiguration(
                                                        event={
                                                            "with": {
                                                                "source": "https://serverlessworkflow.io/samples",
                                                                "type": "io.serverlessworkflow.samples.asyncapi.message.consumed.v1",
                                                                "data": {
                                                                    "message": "${ $message }"
                                                                },
                                                            }
                                                        }
                                                    )
                                                )
                                            }
                                        ],
                                    ),
                                ),
                            )
                        )
                    }
                ],
            )
        case "call-asyncapi-subscribe-consume-until.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="bearer-auth", version="0.1.0"
                ),
                do=[
                    {
                        "getNotifications": CallAsyncApiTask(
                            with_=CallAsyncApiArguments(
                                document={"endpoint": "https://fake.com/docs/asyncapi.json"},
                                channel="/notifications",
                                subscription=AsyncApiSubscription(
                                    filter="${ .correlationId == $context.userId and .payload.from.firstName == $context.contact.firstName and .payload.from.lastName == $context.contact.lastName }",
                                    consume=AsyncApiMessageConsumptionPolicy(
                                        for_={"minutes": 30},
                                        until="${ ($context.consumedMessages | length) == 5 }",
                                    ),
                                ),
                            )
                        )
                    }
                ],
            )
        case "call-asyncapi-subscribe-consume-while.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="bearer-auth", version="0.1.0"
                ),
                do=[
                    {
                        "getNotifications": CallAsyncApiTask(
                            with_=CallAsyncApiArguments(
                                document={"endpoint": "https://fake.com/docs/asyncapi.json"},
                                operation="getNotifications",
                                subscription=AsyncApiSubscription(
                                    filter="${ .correlationId == $context.userId and .payload.from.firstName == $context.contact.firstName and .payload.from.lastName == $context.contact.lastName }",
                                    consume=AsyncApiMessageConsumptionPolicy(
                                        while_="${ ($context.consumedMessages | length) < 5 }"
                                    ),
                                ),
                            )
                        )
                    }
                ],
            )
        case "call-custom-function-cataloged.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="samples",
                    name="call-custom-function-cataloged",
                    version="0.1.0",
                ),
                do=[
                    {
                        "log": CallFunctionTask(
                            call="https://raw.githubusercontent.com/serverlessworkflow/catalog/main/functions/log/1.0.0/function.yaml",
                            with_={
                                "message": "Hello, world!",
                                "level": "information",
                                "timestamp": True,
                                "format": "{TIMESTAMP} [{LEVEL}] ({CONTEXT}): {MESSAGE}",
                            },
                        )
                    }
                ],
            )
        case "call-custom-function-inline.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="samples",
                    name="call-custom-function-inline",
                    version="0.1.0",
                ),
                do=[{"getPet": CallFunctionTask(call="getPetById", with_={"petId": 69})}],
                use={
                    "functions": {
                        "getPetById": {
                            "input": {
                                "schema": {
                                    "document": {
                                        "type": "object",
                                        "properties": {"petId": {"type": "integer"}},
                                        "required": ["petId"],
                                    }
                                }
                            },
                            "call": "http",
                            "with": {
                                "method": "get",
                                "endpoint": "https://petstore.swagger.io/v2/pet/{petId}",
                            },
                        }
                    }
                },
            )
        case "call-grpc.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="grpc-example", version="0.1.0"
                ),
                do=[
                    {
                        "greet": CallGrpcTask(
                            with_=CallGrpcArguments(
                                proto={"endpoint": "file://app/greet.proto"},
                                service=GrpcService(
                                    name="GreeterApi.Greeter", host="localhost", port=5011
                                ),
                                method="SayHello",
                                arguments={"name": "${ .user.preferredDisplayName }"},
                            )
                        )
                    }
                ],
            )
        case "call-mcp.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="mcp-example", version="0.1.0"
                ),
                do=[
                    {
                        "publishMessageToSlack": CallMcpTask(
                            with_=CallMcpArguments(
                                method="tools/call",
                                parameters={
                                    "name": "conversations_add_message",
                                    "arguments": {
                                        "channel_id": "C1234567890",
                                        "thread_ts": "1623456789.123456",
                                        "payload": "Hello, world! :wave:",
                                        "content_type": "text/markdown",
                                    },
                                },
                                transport=McpTransport(
                                    stdio=McpStdioTransport(
                                        command="npx",
                                        arguments=[
                                            "slack-mcp-serverr@latest",
                                            "--transport",
                                            "stdio",
                                        ],
                                        environment={
                                            "SLACK_MCP_XOXP_TOKEN": "xoxp-xv6Cv3jKqNW8esm5YnsftKwIzoQHUzAP"
                                        },
                                    )
                                ),
                            )
                        )
                    }
                ],
            )
        case "call-openapi.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="openapi-example", version="0.1.0"
                ),
                do=[
                    {
                        "findPet": CallOpenApiTask(
                            with_=CallOpenApiArguments(
                                document={
                                    "endpoint": "https://petstore.swagger.io/v2/swagger.json"
                                },
                                operationId="findPetsByStatus",
                                parameters={"status": "available"},
                            )
                        )
                    }
                ],
            )
        case "call-openapi-redirect.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="openapi-example", version="0.1.0"
                ),
                do=[
                    {
                        "findPet": CallOpenApiTask(
                            with_=CallOpenApiArguments(
                                document={
                                    "endpoint": "https://petstore.swagger.io/v2/swagger.json"
                                },
                                operationId="findPetsByStatus",
                                parameters={"status": "available"},
                                redirect=True,
                            )
                        )
                    }
                ],
            )
        case "listen-to-all.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="listen-to-all", version="0.1.0"
                ),
                do=[
                    {
                        "callDoctor": ListenTask(
                            listen=ListenConfiguration(
                                to={
                                    "all": [
                                        {
                                            "with": {
                                                "type": "com.fake-hospital.vitals.measurements.temperature",
                                                "data": "${ .temperature > 38 }",
                                            }
                                        },
                                        {
                                            "with": {
                                                "type": "com.fake-hospital.vitals.measurements.bpm",
                                                "data": "${ .bpm < 60 or .bpm > 100 }",
                                            }
                                        },
                                    ]
                                }
                            )
                        )
                    }
                ],
            )
        case "listen-to-all read-envelope.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="test",
                    name="listen-to-all-read-envelope",
                    version="0.1.0",
                ),
                do=[
                    {
                        "callDoctor": ListenTask(
                            listen=ListenConfiguration(
                                to={
                                    "all": [
                                        {
                                            "with": {
                                                "type": "com.fake-hospital.vitals.measurements.temperature",
                                                "data": "${ .temperature > 38 }",
                                            }
                                        },
                                        {
                                            "with": {
                                                "type": "com.fake-hospital.vitals.measurements.bpm",
                                                "data": "${ .bpm < 60 or .bpm > 100 }",
                                            }
                                        },
                                    ]
                                },
                                read="envelope",
                            )
                        )
                    }
                ],
            )
        case "listen-to-any.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="listen-to-any", version="0.1.0"
                ),
                do=[{"callDoctor": ListenTask(listen=ListenConfiguration(to={"any": []}))}],
            )
        case "listen-to-any-filter.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="listen-to-any-filter", version="0.1.0"
                ),
                do=[
                    {
                        "callDoctor": ListenTask(
                            listen=ListenConfiguration(
                                to={
                                    "any": [
                                        {
                                            "with": {
                                                "type": "com.fake-hospital.vitals.measurements.temperature",
                                                "data": "${ .temperature > 38 }",
                                            }
                                        },
                                        {
                                            "with": {
                                                "type": "com.fake-hospital.vitals.measurements.bpm",
                                                "data": "${ .bpm < 60 or .bpm > 100 }",
                                            }
                                        },
                                    ]
                                }
                            )
                        )
                    }
                ],
            )
        case "listen-to-any-forever-foreach.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="test",
                    name="listen-to-any-while-foreach",
                    version="0.1.0",
                ),
                do=[
                    {
                        "listenToGossips": ListenTask(
                            listen=ListenConfiguration(to={"any": [], "until": "${ false }"}),
                            foreach={
                                "item": "event",
                                "at": "i",
                                "do": [
                                    {
                                        "postToChatApi": CallHttpTask(
                                            with_=CallHttpArguments(
                                                method="post",
                                                endpoint="https://fake-chat-api.com/room/{roomId}",
                                                body={"event": "${ $event }"},
                                            )
                                        )
                                    }
                                ],
                            },
                        )
                    }
                ],
            )
        case "listen-to-any-until-condition.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="listen-to-any", version="0.1.0"
                ),
                do=[
                    {
                        "callDoctor": ListenTask(
                            listen=ListenConfiguration(
                                to={"any": [], "until": "( . | length ) > 3"}
                            )
                        )
                    }
                ],
            )
        case "listen-to-any-until-consumed.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="listen-to-any", version="0.1.0"
                ),
                do=[
                    {
                        "callDoctor": ListenTask(
                            listen=ListenConfiguration(
                                to={
                                    "any": [
                                        {
                                            "with": {
                                                "type": "com.fake-hospital.vitals.measurements.temperature",
                                                "data": "${ .temperature > 38 }",
                                            }
                                        },
                                        {
                                            "with": {
                                                "type": "com.fake-hospital.vitals.measurements.bpm",
                                                "data": "${ .bpm < 60 or .bpm > 100 }",
                                            }
                                        },
                                    ],
                                    "until": {
                                        "one": {
                                            "with": {
                                                "type": "com.fake-hospital.patient.checked-out"
                                            }
                                        }
                                    },
                                }
                            )
                        )
                    }
                ],
            )
        case "mock-service-extension.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="sample-workflow", version="0.1.0"
                ),
                do=[
                    {
                        "callHttp": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get", endpoint={"uri": "https://fake.com/sample"}
                            )
                        )
                    }
                ],
                use={
                    "extensions": [
                        {
                            "mockService": {
                                "extend": "call",
                                "when": '($task.with.endpoint != null and ($task.with.endpoint | startswith("https://mocked.service.com"))) or ($task.with.endpoint.uri != null and ($task.with.endpoint.uri | startswith("https://mocked.service.com")))',
                                "before": [
                                    {
                                        "mockResponse": {
                                            "set": {
                                                "statusCode": 200,
                                                "headers": {"Content-Type": "application/json"},
                                                "content": {"foo": {"bar": "baz"}},
                                            },
                                            "then": "exit",
                                        }
                                    }
                                ],
                            }
                        }
                    ]
                },
            )
        case "raise-reusable.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="raise-not-implemented", version="0.1.0"
                ),
                do=[
                    {"notImplemented": RaiseTask(raise_=RaiseConfiguration(error="notImplemented"))}
                ],
                use={
                    "errors": {
                        "notImplemented": {
                            "type": "https://serverlessworkflow.io/errors/not-implemented",
                            "status": 500,
                            "title": "Not Implemented",
                            "detail": "${ \"The workflow '\\( $workflow.definition.document.name ):\\( $workflow.definition.document.version )' is a work in progress and cannot be run yet\" }",
                        }
                    }
                },
            )
        case "run-container.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="run-container", version="0.1.0"
                ),
                do=[
                    {
                        "runContainer": RunTask(
                            run=RunConfiguration(
                                container=ContainerConfiguration(image="hello-world")
                            )
                        )
                    }
                ],
            )
        case "run-container-cleanup-always.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="run-container", version="0.1.0"
                ),
                do=[
                    {
                        "runContainer": RunTask(
                            run=RunConfiguration(
                                container=ContainerConfiguration(
                                    image="hello-world",
                                    lifetime=ContainerLifetime(cleanup="always"),
                                )
                            )
                        )
                    }
                ],
            )
        case "run-container-cleanup-eventually.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="run-container", version="0.1.0"
                ),
                do=[
                    {
                        "runContainer": RunTask(
                            run=RunConfiguration(
                                container=ContainerConfiguration(
                                    image="hello-world",
                                    lifetime=ContainerLifetime(
                                        cleanup="eventually", after={"minutes": 30}
                                    ),
                                )
                            )
                        )
                    }
                ],
            )
        case "run-container-stdin-and-arguments.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="test",
                    name="run-container-stdin-and-arguments",
                    version="0.1.0",
                ),
                do=[
                    {"setInput": SetTask(set={"message": "Hello World"})},
                    {
                        "runContainer": RunTask(
                            input=Input(from_="${ .message }"),
                            run=RunConfiguration(
                                container=ContainerConfiguration(
                                    image="alpine",
                                    command='input=$(cat)\necho "STDIN was: $input"\necho "ARGS are $1 $2"\n',
                                    stdin="${ . }",
                                    arguments=["Foo", "Bar"],
                                )
                            ),
                        )
                    },
                ],
            )
        case "run-container-with-name.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="run-container-with-name", version="0.1.0"
                ),
                do=[
                    {
                        "runContainer": RunTask(
                            run=RunConfiguration(
                                container=ContainerConfiguration(
                                    image="hello-world",
                                    name='${ "hello-\\(.workflow.document.name)-\\(.task.name)-\\(.workflow.id)" }',
                                )
                            )
                        )
                    }
                ],
            )
        case "run-return-all.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="run-container", version="0.1.0"
                ),
                do=[
                    {
                        "runContainer": RunTask(
                            run=RunConfiguration(
                                container=ContainerConfiguration(image="hello-world"), return_="all"
                            )
                        )
                    }
                ],
            )
        case "run-return-code.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="run-container", version="0.1.0"
                ),
                do=[
                    {
                        "runContainer": RunTask(
                            run=RunConfiguration(
                                container=ContainerConfiguration(image="hello-world"),
                                return_="code",
                            )
                        )
                    }
                ],
            )
        case "run-return-none.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="run-container", version="0.1.0"
                ),
                do=[
                    {
                        "runContainer": RunTask(
                            run=RunConfiguration(
                                container=ContainerConfiguration(image="hello-world"),
                                return_="none",
                            )
                        )
                    }
                ],
            )
        case "run-return-stderr.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="run-container", version="0.1.0"
                ),
                do=[
                    {
                        "runContainer": RunTask(
                            run=RunConfiguration(
                                container=ContainerConfiguration(image="hello-world"),
                                return_="stderr",
                            )
                        )
                    }
                ],
            )
        case "run-script-with-stdin-and-arguments.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="examples",
                    name="run-script-with-stdin-and-arguments",
                    version="1.0.0",
                ),
                do=[
                    {
                        "runScript": RunTask(
                            run=RunConfiguration(
                                script=ScriptConfiguration(
                                    language="javascript",
                                    stdin="Hello Workflow",
                                    environment={"foo": "bar"},
                                    arguments=["hello"],
                                    code="// Reading Input from STDIN\nimport { readFileSync } from 'node:fs';\nconst stdin = readFileSync(process.stdin.fd, 'utf8');\nconsole.log('stdin > ', stdin) // Output: stdin > Hello Workflow\n\n// Reading from argv\nconst [_, __, arg] = process.argv;\nconsole.log('arg > ', arg) // Output: arg > hello\n\n// Reading from env\nconst foo = process.env.foo;\nconsole.log('env > ', foo) // Output: env > bar\n",
                                )
                            )
                        )
                    }
                ],
            )
        case "run-shell-stdin-and-arguments.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2",
                    namespace="examples",
                    name="run-shell-with-stdin-and-arguments",
                    version="1.0.0",
                ),
                do=[
                    {"setInput": SetTask(set={"message": "Hello World"})},
                    {
                        "runShell": RunTask(
                            input=Input(from_="${ .message }"),
                            run=RunConfiguration(
                                shell=ShellConfiguration(
                                    stdin="${ . }",
                                    command='input=$(cat)\necho "STDIN was: $input"\necho "ARGS are $1 $2"\n',
                                    arguments=["Foo", "Bar"],
                                )
                            ),
                        )
                    },
                ],
            )
        case "run-subflow.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="run-subflow", version="0.1.0"
                ),
                do=[
                    {
                        "registerCustomer": RunTask(
                            run=RunConfiguration(
                                workflow=WorkflowConfiguration(
                                    namespace="test",
                                    name="register-customer",
                                    version="0.1.0",
                                    input={"customer": ".user"},
                                )
                            )
                        )
                    }
                ],
            )
        case "schedule-cron.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="cron-schedule", version="0.1.0"
                ),
                schedule=Schedule(cron="0 0 * * *"),
                do=[
                    {
                        "backup": CallHttpTask(
                            with_=CallHttpArguments(
                                method="post", endpoint="https://example.com/api/v1/backup/start"
                            )
                        )
                    }
                ],
            )
        case "schedule-event-driven.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="event-driven-schedule", version="0.1.0"
                ),
                schedule={
                    "on": {
                        "one": {
                            "with": {"type": "com.example.hospital.events.patients.heartbeat.low"}
                        }
                    }
                },
                do=[
                    {
                        "callNurse": CallHttpTask(
                            with_=CallHttpArguments(
                                method="post",
                                endpoint="https://hospital.example.com/api/v1/notify",
                                body={
                                    "patientId": "${ $workflow.input[0].data.patient.id }",
                                    "patientName": "${ $workflow.input[0].data.patient.name }",
                                    "roomNumber": "${ $workflow.input[0].data.patient.room.number }",
                                    "vitals": {
                                        "heartRate": "${ $workflow.input[0].data.patient.vitals.bpm }",
                                        "timestamp": "${ $workflow.input[0].data.timestamp }",
                                    },
                                    "message": "Alert: Patient's heartbeat is critically low. Immediate attention required.",
                                },
                            )
                        )
                    }
                ],
            )
        case "star-wars-homeworld.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="examples", name="star-wars-homeplanet", version="1.0.0"
                ),
                input={
                    "schema": {
                        "format": "json",
                        "document": {
                            "type": "object",
                            "required": ["id"],
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "description": "The id of the star wars character to get",
                                    "minimum": 1,
                                }
                            },
                        },
                    }
                },
                do=[
                    {
                        "getStarWarsCharacter": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get",
                                endpoint="https://swapi.dev/api/people/{id}",
                                output="response",
                            ),
                            export=Export(as_={"homeworld": "${ .content.homeworld }"}),
                        )
                    },
                    {
                        "getStarWarsHomeworld": CallHttpTask(
                            with_=CallHttpArguments(
                                method="get", endpoint="${ $context.homeworld }"
                            )
                        )
                    },
                ],
            )
        case "switch-then-string.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="test", name="sample-workflow", version="0.1.0"
                ),
                do=[
                    {
                        "processOrder": SwitchTask(
                            switch=[
                                {
                                    "case1": SwitchCase(
                                        when='.orderType == "electronic"',
                                        then="processElectronicOrder",
                                    )
                                },
                                {
                                    "case2": SwitchCase(
                                        when='.orderType == "physical"', then="processPhysicalOrder"
                                    )
                                },
                                {"default": SwitchCase(then="handleUnknownOrderType")},
                            ]
                        )
                    },
                    {
                        "processElectronicOrder": SetTask(
                            set={"validate": True, "status": "fulfilled"}, then="exit"
                        )
                    },
                    {
                        "processPhysicalOrder": SetTask(
                            set={"inventory": "clear", "items": 1, "address": "Elmer St"},
                            then="exit",
                        )
                    },
                    {
                        "handleUnknownOrderType": SetTask(
                            set={"log": "warn", "message": "something's wrong"}
                        )
                    },
                ],
            )
        case "try-catch.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="default", name="try-catch", version="0.1.0"
                ),
                do=[
                    {
                        "tryGetPet": TryTask(
                            try_=[
                                {
                                    "getPet": CallHttpTask(
                                        with_=CallHttpArguments(
                                            method="get",
                                            endpoint="https://petstore.swagger.io/v2/pet/{petId}",
                                        )
                                    )
                                }
                            ],
                            catch=CatchConfiguration(
                                errors={
                                    "with": {
                                        "type": "https://serverlessworkflow.io/spec/1.0.0/errors/communication",
                                        "status": 404,
                                    }
                                }
                            ),
                        )
                    }
                ],
            )
        case "try-catch-retry-inline.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="default", name="try-catch-retry", version="0.1.0"
                ),
                do=[
                    {
                        "tryGetPet": TryTask(
                            try_=[
                                {
                                    "getPet": CallHttpTask(
                                        with_=CallHttpArguments(
                                            method="get",
                                            endpoint="https://petstore.swagger.io/v2/pet/{petId}",
                                        )
                                    )
                                }
                            ],
                            catch=CatchConfiguration(
                                errors={
                                    "with": {
                                        "type": "https://serverlessworkflow.io/spec/1.0.0/errors/communication",
                                        "status": 503,
                                    }
                                },
                                retry={
                                    "delay": {"seconds": 3},
                                    "backoff": {"exponential": {}},
                                    "limit": {"attempt": {"count": 5}},
                                },
                            ),
                        )
                    }
                ],
            )
        case "try-catch-retry-reusable.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="default", name="try-catch-retry", version="0.1.0"
                ),
                do=[
                    {
                        "tryGetPet": TryTask(
                            try_=[
                                {
                                    "getPet": CallHttpTask(
                                        with_=CallHttpArguments(
                                            method="get",
                                            endpoint="https://petstore.swagger.io/v2/pet/{petId}",
                                        )
                                    )
                                }
                            ],
                            catch=CatchConfiguration(
                                errors={
                                    "with": {
                                        "type": "https://serverlessworkflow.io/spec/1.0.0/errors/communication",
                                        "status": 503,
                                    }
                                },
                                retry="default",
                            ),
                        )
                    }
                ],
                use={
                    "retries": {
                        "default": {
                            "delay": {"seconds": 3},
                            "backoff": {"exponential": {}},
                            "limit": {"attempt": {"count": 5}},
                        }
                    }
                },
            )
        case "try-catch-then.yaml":
            new_workflow = Workflow(
                document=Document(
                    dsl="1.0.2", namespace="default", name="try-catch", version="0.1.0"
                ),
                do=[
                    {
                        "tryGetPet": TryTask(
                            try_=[
                                {
                                    "getPet": CallHttpTask(
                                        with_=CallHttpArguments(
                                            method="get",
                                            endpoint="https://petstore.swagger.io/v2/pet/{petId}",
                                        )
                                    )
                                }
                            ],
                            catch=CatchConfiguration(
                                errors={
                                    "with": {
                                        "type": "https://serverlessworkflow.io/spec/1.0.0/errors/communication",
                                        "status": 404,
                                    }
                                },
                                as_="error",
                                do=[
                                    {
                                        "notifySupport": EmitTask(
                                            emit=EmitConfiguration(
                                                event={
                                                    "with": {
                                                        "source": "https://petstore.swagger.io",
                                                        "type": "io.swagger.petstore.events.pets.not-found.v1",
                                                        "data": "${ $error }",
                                                    }
                                                }
                                            )
                                        )
                                    },
                                    {
                                        "setError": SetTask(
                                            set={"error": "$error"},
                                            export=Export(as_="$context + { error: $error }"),
                                        )
                                    },
                                ],
                            ),
                        )
                    },
                    {
                        "buyPet": CallHttpTask(
                            if_="$context.error == null",
                            with_=CallHttpArguments(
                                method="put",
                                endpoint="https://petstore.swagger.io/v2/pet/{petId}",
                                body='${ . + { status: "sold" } }',
                            ),
                        )
                    },
                ],
            )
        case _:
            print("No specific test logic for this example.")
            # fail
            raise AssertionError(f"No test logic defined for {example_file.name}")

    # Compare serialized versions for better diff output
    baseline_serialized = baseline_workflow.serialize()
    new_serialized = new_workflow.serialize()

    if baseline_serialized != new_serialized:
        import json

        print("\n=== BASELINE (from YAML) ===")
        print(json.dumps(baseline_serialized, indent=2, default=str))
        print("\n=== NEW (constructed) ===")
        print(json.dumps(new_serialized, indent=2, default=str))

    assert baseline_serialized == new_serialized
