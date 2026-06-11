from app.agent import graph
test = graph.invoke({
    "question": "Hi"
})
# یا اگر کلید ساده‌تری مانند input دارید:
# test = graph.invoke({"input": "Hi"})
print(test)



