from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List
import traceback

from evaluate import evaluate_specific_user  # 信任评估主逻辑

app = FastAPI()

class TriggerRequest(BaseModel):
    user_id: str = Field(..., description="用户ID")
    terminal_ids: List[str] = Field(..., description="终端ID列表")
    vm_ids: List[str] = Field(..., description="虚拟机ID列表")

#注册下面的validation_exception_handler函数处理RequestValidationError问题
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    field = exc.errors()[0]["loc"][-1]
    return JSONResponse(
        status_code=422,
        content={
            "code": 4001,
            "status": "fail",
            "data": {
                "field": field,
                "reason": "字段缺失",
                "message": f"缺失字段：{field}"
            }
        }
    )

@app.post("/api/v1/trust/trigger")
def trigger_trust_evaluation(req: TriggerRequest):
    try:
        result_dict = evaluate_specific_user(
            req.user_id, req.terminal_ids, req.vm_ids
        )

        response = {
            "code": 2000,
            "status": "succeed",
            "data": [
                {
                    "user_id ": user_id,
                    "trust_result": {
                        "score": trust_information["score"],
                        "action": trust_information["action"]
                    },
                    "message": "评估已完成"
                }
                for user_id, trust_information in result_dict
            ]
        }
        return response

    except Exception:
        return {
            "code": 5000,
            "status": "fail",
            "data": {
                "message": traceback.format_exc()
            }
        }

# 启动方式（命令行运行）：
# uvicorn trust_api:app --reload --port 8080
