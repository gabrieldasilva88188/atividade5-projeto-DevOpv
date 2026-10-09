"""Teste de performance com Locust.

Simula usuários que criam, listam, consultam e concluem tarefas.
Ao final, valida limites (SLOs) e define o código de saída:
  - P95_MS            : latência P95 máxima em ms        (padrão 500)
  - MAX_FAIL_RATIO    : proporção máxima de falhas       (padrão 0.01 = 1%)
  - MIN_RPS           : vazão mínima em req/s            (padrão 20)
"""
import os
import random

from locust import HttpUser, between, events, task

P95_MS = float(os.environ.get("P95_MS", "500"))
MAX_FAIL_RATIO = float(os.environ.get("MAX_FAIL_RATIO", "0.01"))
MIN_RPS = float(os.environ.get("MIN_RPS", "20"))


class TaskUser(HttpUser):
    wait_time = between(0.05, 0.2)

    def on_start(self):
        self.task_ids = []

    @task(3)
    def create_task(self):
        with self.client.post(
            "/tasks",
            json={"title": f"Tarefa {random.randint(1, 10_000)}", "priority": "low", "tags": ["perf"]},
            name="POST /tasks",
            catch_response=True,
        ) as resp:
            if resp.status_code == 201:
                self.task_ids.append(resp.json()["id"])
                resp.success()
            else:
                resp.failure(f"status inesperado: {resp.status_code}")

    @task(5)
    def list_tasks(self):
        self.client.get("/tasks?status=open", name="GET /tasks")

    @task(3)
    def get_task(self):
        if self.task_ids:
            self.client.get(f"/tasks/{random.choice(self.task_ids)}", name="GET /tasks/:id")

    @task(2)
    def complete_task(self):
        if self.task_ids:
            self.client.patch(f"/tasks/{random.choice(self.task_ids)}/complete", name="PATCH /tasks/:id/complete")

    @task(1)
    def stats(self):
        self.client.get("/stats", name="GET /stats")


@events.quitting.add_listener
def check_thresholds(environment, **_kwargs):
    total = environment.stats.total
    problems = []

    if total.num_requests == 0:
        problems.append("nenhuma requisição foi executada")
    else:
        if total.fail_ratio > MAX_FAIL_RATIO:
            problems.append(f"taxa de falhas {total.fail_ratio:.2%} > {MAX_FAIL_RATIO:.2%}")
        p95 = total.get_response_time_percentile(0.95)
        if p95 > P95_MS:
            problems.append(f"P95 {p95:.0f} ms > {P95_MS:.0f} ms")
        if total.total_rps < MIN_RPS:
            problems.append(f"vazão {total.total_rps:.1f} req/s < {MIN_RPS:.0f} req/s")

    if problems:
        print("\n[PERFORMANCE] FALHOU:\n  - " + "\n  - ".join(problems))
        environment.process_exit_code = 1
    else:
        print(
            f"\n[PERFORMANCE] OK: {total.num_requests} req, "
            f"P95={total.get_response_time_percentile(0.95):.0f} ms, "
            f"falhas={total.fail_ratio:.2%}, vazão={total.total_rps:.1f} req/s"
        )
        environment.process_exit_code = 0
