.PHONY: build-image

image_name=$(or ${IMAGE_NAME}, aws-blog-scraper)
image_version=$(or ${IMAGE_VERSION}, 1.0)

build-image:
	docker build --rm -f "Dockerfile" -t "${image_name}:${image_version}" "."

exec-docker:
	docker run 