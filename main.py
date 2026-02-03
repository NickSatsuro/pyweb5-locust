import time
import grpc
from locust import User, HttpUser, task, between, constant, events

import glossary_pb2 as pb2
import glossary_pb2_grpc as pb2_grpc

class GrpcClient:
    def __init__(self, host):
        self.channel = grpc.insecure_channel(host)
        self.stub = pb2_grpc.GlossaryServiceStub(self.channel)

    def call_method(self, method_name, request_func, request_data):
        start_time = time.time()
        result =  None
        try:
            result = request_func(request_data)
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) *1000)
            events.request.fire(
                request_type='gRPC', 
                name = method_name, 
                response_time = total_time, 
                exception=e,
                response_length = 0,
            )
        else:
            total_time = int((time.time() - start_time) *1000)
            events.request.fire(
                request_type='gRPC', 
                name = method_name, 
                response_time = total_time, 
                response_length = 0,
            )

    def close(self):
        self.channel.close()


class GlossaryGrpcUser(User):
    wait_time = constant(1)

    def on_start(self):
        self.client = GrpcClient("83.166.254.54:50051")

    def on_stop(self):
        return super().on_stop()
    
    @task(3)
    def get_all_terms(self):
        req = pb2.Empty()
        self.client.call_method("GetTerms", self.client.stub.GetTerms, req)


    @task(1)
    def get_one_term(self):
        req = pb2.GetTermRequest(id=1)
        self.client.call_method("GetTerm", self.client.stub.GetTerm, req)


class GlossaryRestUser(HttpUser):
    wait_time = constant(1)
    host = "http://83.166.254.54:8000"

    @task(3) 
    def get_all_terms_rest(self):
        self.client.get("/api/terms", name="/api/terms")

    @task(1)
    def get_one_term_rest(self):
        self.client.get("/api/terms/1", name="/api/terms/{id}")

