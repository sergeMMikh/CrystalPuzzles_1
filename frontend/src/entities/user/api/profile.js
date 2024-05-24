import { $authHost } from '@shared/api/axios.instances';

const getProfile = async () => {
	const { data } = await $authHost.get('/profile');
	return data;
};

const getProfileEdit = async () => {
	const { data } = await $authHost.get('/profile/edit');
	return data;
};

const updateProfile = async (profile) => {
	const { firstname, lastname, surname, birthday, is_man, contact } = profile;
	const { data } = await $authHost.put('/profile/edit', {
		firstname,
		lastname,
		surname,
		birthday,
		is_man,
		contact
	});
	return data;
};

const updateProfileAvatar = async (avatar) => {
	const formData = new FormData();
	formData.append('file', avatar);

	const { data } = await $authHost.put('/profile/set-photo', formData);
	return data;
};

const deleteProfileAvatar = async () => {
	const { data } = await $authHost.delete('/profile/set-photo');
	return data;
};

const getProfileAvatar = async () => {
	const { data } = await $authHost.get('/profile/get-photo');
	return data;
};

export {
	getProfile,
	getProfileEdit,
	updateProfile,
	updateProfileAvatar,
	deleteProfileAvatar,
	getProfileAvatar
};
