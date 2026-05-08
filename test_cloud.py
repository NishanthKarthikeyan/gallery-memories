import cloudinary
import cloudinary.api
import cloudinary.uploader

cloudinary.config(
  cloud_name = "dza7ugm28",
  api_key = "993526995564523",
  api_secret = "y8cF4Q8doECvTCYtp7gVdX7S8ug",
  secure = True
)

try:
    result = cloudinary.Search().expression("folder:family_vault/*").max_results(5).execute()
    print("Found resources:", len(result.get('resources', [])))
    for r in result.get('resources', []):
        print(r['public_id'])
except Exception as e:
    print("Error:", e)
